"""
Sample E-Commerce REST API built with FastAPI.
Demonstrates Pydantic models, path parameters, query filters, JWT auth dependencies, and responses.
"""

from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="CloudCommerce API",
    description="High-performance multi-tenant e-commerce backend service.",
    version="2.4.0"
)


# --- Pydantic Data Models ---
class ProductCreate(BaseModel):
    name: str = Field(..., example="Wireless Noise Cancelling Headphones")
    description: Optional[str] = Field(None, example="Premium over-ear Bluetooth headphones")
    price: float = Field(..., gt=0, example=249.99)
    category: str = Field(..., example="Electronics")
    inventory: int = Field(default=0, ge=0, example=150)


class ProductResponse(ProductCreate):
    id: int = Field(..., example=101)
    is_active: bool = Field(default=True)


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]
    shipping_address: str


# --- Dummy Auth Dependency ---
def get_current_user(token: str = "Bearer demo-token"):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"user_id": 42, "role": "admin"}


# --- API Routes ---
@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def list_products(
    category: Optional[str] = Query(None, description="Filter products by category"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Retrieve Paginated Products.
    Allows clients to filter the catalog by category and price range with pagination controls.
    """
    return []


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a New Product.
    Requires Admin authentication. Validates product fields and inventory stock.
    """
    return {
        "id": 101,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "inventory": product.inventory,
        "is_active": True
    }


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product_by_id(product_id: int):
    """
    Get Product Details by ID.
    Retrieves full SKU information, pricing, and availability.
    """
    return {
        "id": product_id,
        "name": "Sample Product",
        "description": "Details",
        "price": 99.99,
        "category": "General",
        "inventory": 10,
        "is_active": True
    }


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Soft-Delete Product.
    Requires Admin privileges. Disables the specified catalog entry.
    """
    return None


@app.post("/orders", status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit Customer Order.
    Requires authenticated session. Deducts stock and creates an order confirmation.
    """
    return {"order_id": "ORD-9902", "status": "PENDING_PAYMENT"}


@app.get("/health", tags=["System"])
def health_check():
    """
    Liveness and Health Probe.
    Returns 200 OK when cluster pods and database pools are operational.
    """
    return {"status": "healthy", "service": "CloudCommerce API"}
