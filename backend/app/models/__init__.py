# This imports the User model so SQLAlchemy can register the users table.
from app.models.user import User
# This imports the Stock model so SQLAlchemy can register the stocks table.
from app.models.stock import Stock
# This imports the Price model so SQLAlchemy can register the prices table.
from app.models.price import Price
# This imports the Order model so SQLAlchemy can register the orders table.
from app.models.order import Order
# This imports the Trade model so SQLAlchemy can register the trades table.
from app.models.trade import Trade
# This imports the Portfolio model so SQLAlchemy can register the portfolio table.
from app.models.portfolio import Portfolio
# This imports the Watchlist model so SQLAlchemy can register the watchlists table.
from app.models.watchlist import Watchlist
# This imports the WatchlistItem model so SQLAlchemy can register the watchlist_items table.
from app.models.watchlistitem import WatchlistItem
# This imports the UserProfile model so SQLAlchemy can register the user_profiles table.
from app.models.userprofile import UserProfile
# This imports the Role model so SQLAlchemy can register the roles table.
from app.models.role import Role
# This imports the UserRole model so SQLAlchemy can register the user_roles table.
from app.models.userrole import UserRole
# This imports the News model so SQLAlchemy can register the news table.
from app.models.news import News
# This imports the SentimentAnalysis model so SQLAlchemy can register the sentiment_analysis table.
from app.models.sentimentanalysis import SentimentAnalysis