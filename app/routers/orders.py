"""
This module defines the data models for the recipe application.
"""
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.orders import Bill, Cart, ProductCatalogue
from app.schema.orders import IngredientListBase, BillBase, BillResponse, ShopListBase
from app.core.database import engine, get_db, Base, DbDependency

Base.metadata.create_all(bind=engine)
router = APIRouter()


@router.get("/bills/{bill_no}", response_model=BillResponse)
async def get_bill(bill_no: int, db: DbDependency):
    """Get a bill by its bill number with all associated ingredients"""
    bill = db.query(Bill).filter(Bill.bill_no == bill_no).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return {
        "bill_no": bill.bill_no,
        "bill_date": bill.bill_date.strftime("%Y-%m-%d"),
        "num_items": bill.num_items,
        "ingredients": [
            {
                "name": cart.name,
                "quantity": cart.quantity
            }
            for cart in bill.cart
        ]
    }

@router.post("/add_items")
async def add_items(shop_list: ShopListBase, db: DbDependency):
    """Create a new bill with summed quantities"""
    try:
        # Generate bill number
        max_bill_no = db.query(func.max(Bill.bill_no)).scalar() or 0
        new_bill_no = max_bill_no + 1

        # Calculate TOTAL quantity (sum of all items)
        total_qty = sum(item.quantity for item in shop_list.ingredient_list)

        # Create bill with total quantity
        db_bill = Bill(
            bill_no=new_bill_no,
            num_items=total_qty  # This should be sum of quantities
        )
        db.add(db_bill)
        db.flush()

        # Add cart items
        # db_cart_items = []
        for ing in shop_list.ingredient_list:
            product = db.query(ProductCatalogue).filter(ProductCatalogue.id == ing.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with ID {ing.product_id} not found!!!")

        db_cart_items = [
            Cart(
                name=ing.name,
                product_id = ing.product_id,
                quantity=ing.quantity,  # Ensure this matches request field
                bill_id=db_bill.id,
                mrp = product.mrp,
                total = ing.quantity * product.mrp
                )
        ]
        db.add_all(db_cart_items)
        
        db.commit()
        
        db.refresh(db_bill)
        return {
            "bill_no": db_bill.bill_no,
            "cart_items": [
                {
                    "name": item.name, 
                    "product_id":item.product_id, 
                    "quantity": item.quantity,
                    "mrp": item.product.mrp
                }
                for item in db_cart_items
            ]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) # pylint: disable=raise-missing-from
    


@router.post("/upload_catalogue")
async def upload_catalogue(db: DbDependency, file: UploadFile = File(...)):
    """Upload a catalogue of products with their prices"""
    try:
        if file.filename.endswith(".csv"):
            df: pd.DataFrame = pd.read_csv(file.file)
        elif file.filename.endswith([".xlsx", ".xlx"]):
            df: pd.DataFrame = pd.read_excel(file.file, engine="openpyxl")
        else:
            raise HTTPException(status_code=415, detail = "Unsupported file format. Only CSV, XLSX and XLS files are supported")

        required_columns = {"product_name", "brand", "mrp", "pack_size", "category"}
        df.columns = df.columns.str.lower()
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(status_code=400, detail="Missing required columns")

        # Convert DataFrame to list of dictionaries
        products = df.to_dict(orient="records")
        db.bulk_insert_mappings(ProductCatalogue, products)
        db.commit()
        return {"message": f"Successfully uploaded {len(products)} products"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # pylint: disable=raise-missing-from
