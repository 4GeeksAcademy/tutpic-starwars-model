from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()


favorite_characters = Table(
    "favorite_characters",
    db.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
)

favorite_planets = Table(
    "favorite_planets",
    db.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("planet_id", ForeignKey("planets.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_characters: Mapped[List["Character"]] = relationship(
        secondary=favorite_characters, back_populates="user_favorites")

    favorite_planets: Mapped[List["Planet"]] = relationship(
        secondary=favorite_planets, back_populates="user_favorites")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    def serialize_favs(self):
        return {
            "favorite_characters": list(map(lambda x:x.serialize(),self.favorite_characters)),
            "favorite_planets": list(map(lambda x:x.serialize(),self.favorite_planets))
        }



class Character(db.Model):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(15))
    weight: Mapped[int] = mapped_column(Integer)
    skin_color: Mapped[str] = mapped_column(String(15))
    hair_color: Mapped[str] = mapped_column(String(15))
    eye_color: Mapped[str] = mapped_column(String(15))

    user_favorites: Mapped[List[User]] = relationship(
        secondary=favorite_characters, back_populates="favorite_characters")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "weight": self.weight,
            "skin_color": self.skin_color,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color
        }
    def serialize_favs(self):
        return {
            "user_favorites":list(map(lambda x: x.serialize(),self.user_favorites))
        }


class Planet(db.Model):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True)
    gravity: Mapped[str] = mapped_column(String(20))
    population: Mapped[int] = mapped_column(Integer)
    diameter: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(30))
    climate: Mapped[str] = mapped_column(String(15))
    terrain: Mapped[str] = mapped_column(String(15))
    rotation_period:  Mapped[int] = mapped_column(Integer)

    user_favorites: Mapped[List[User]] = relationship(
        secondary=favorite_planets, back_populates="favorite_planets"
    )

    def serialize(self):
        return {
            "id": self.id,
            "gravity": self.gravity,
            "population": self.population,
            "diameter": self.diameter,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "rotation_period": self.rotation_period
        }
    def serialize_favs(self):
        return {
            "user_favorites":list(map(lambda x: x.serialize(),self.user_favorites))
        }