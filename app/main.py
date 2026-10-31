import logging
import time
from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Expense
from app.rates import RatesUnavailable, get_rate
from app.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("expense-tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    took_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "%s %s status=%s took=%.1fms",
        request.method, request.url.path, response.status_code, took_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logger.exception("unhandled error on %s %s",
                     request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        logger.exception("database reachable nahi hai")
        db_ok = False

    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={"status": "ok" if db_ok else "degraded", "database": db_ok},
    )


@app.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.scalars(select(Expense)).all()


@app.get("/expenses/summary")
async def summary(
    currency: str = Query(default="INR", min_length=3, max_length=3),
    db: Session = Depends(get_db),
):
    rows = db.scalars(select(Expense)).all()
    total = sum((row.amount for row in rows), Decimal("0"))

    by_category: dict[str, Decimal] = {}
    for row in rows:
        by_category[row.category] = by_category.get(
            row.category, Decimal("0")) + row.amount

    try:
        rate = await get_rate(settings.base_currency, currency)
        converted = True
    except RatesUnavailable:
        rate = 1.0
        currency = settings.base_currency
        converted = False

    return {
        "currency": currency.upper(),
        "converted": converted,
        "count": len(rows),
        "total": round(float(total) * rate, 2),
        "by_category": {k: round(float(v) * rate, 2) for k, v in by_category.items()},
    }


@app.get("/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=404, detail=f"Expense {expense_id} not found")
    return expense


@app.patch("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=404, detail=f"Expense {expense_id} not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=404, detail=f"Expense {expense_id} not found")
    db.delete(expense)
    db.commit()
