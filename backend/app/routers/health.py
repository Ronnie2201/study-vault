from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from  ..database import get_db

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
   """
   Health check endpoint.

   Returns the application status and database connectivity.
   This endpoint is used by load balancers and monitoring tools.
   """
   try: 
      # Execute a simple query to vrify database connectivity
      db.execute(text("SELECT 1"))
      db_status = "healthy"
   except Exception as e:
      db_status = f"unhealthy: {str(e)}"

   return {
      "status": "ok",
      "database": db_status,
      "version": "0.1.0",
   }
