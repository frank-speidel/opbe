from contextlib import asynccontextmanager
from typing import Any, Optional
from fastapi import FastAPI, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, select
from .db import init_db, get_session


@asynccontextmanager
async def life_span(app: FastAPI):
    print("RUNING")
    init_db()
    yield
    print("STOPPED")
    

app = FastAPI(
    title="OnePlace",
    description="A simple e-commerce application",
    version="1.0.0",
    lifespan=life_span
)


"""
CORS
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
SCHEMAS
"""
class MenuItem(BaseModel):
    title: str
    icon: Optional[str] = None
    link: Optional[str] = None
    childs: "Optional[list[MenuItem]]" = None

class MenuGroup(BaseModel):
    title: str
    menu_items: Optional[list[MenuItem]]=None
    
    
class NavigationNode(SQLModel, table=True):
    __tablename__ = 'navigation'
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    
    title: str
    icon: Optional[str] = None
    link: Optional[str] = None
    
    parent_id: Optional[int] = Field(
        foreign_key='navigation.id',
        default=None,
        nullable=True
    )
    
    parent: Optional['NavigationNode'] = Relationship(
        back_populates='children',
        sa_relationship_kwargs=dict(
            remote_side='NavigationNode.id'
        )
    )
    
    children: list['NavigationNode'] = Relationship(
        back_populates='parent'
    )
    
    
        



@app.get("/hello/{name}")
async def hello(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/navigation")
async def get_navigation() -> Any:
    session: Session = Depends(get_session)
    
    heroes = session.exec(select(NavigationNode)).all()
    
    
    menuitems: list[MenuItem] = []
    menuitems.append(MenuItem(title="Kontakte"))
    menuitems.append(MenuItem(title="Produkte"))
    menuitems.append(MenuItem(title="Kunden"))
    menuitems.append(MenuItem(title="Lieferanten"))
    
    menuroot = MenuItem(title="Stammdaten", childs=menuitems)
                     
    return menuroot.model_dump_json() #dict(exclude=True)