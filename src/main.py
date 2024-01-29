from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_PASSWORD, DB_NAME, DB_HOST, DB_USER
from src.DatabaseModel import Base
from Handlers.TransactionsHandler import TransactionHandler
from Handlers.UserHandler import UserHandler
from Handlers.WalletHandler import WalletHandler
from TaskMethods import Task
from UserInterface import UserInterface

# create_db----------------------------------------------------------------------------------------------------------------------------------
db_path = f'{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
engine = create_engine(f'postgresql+psycopg2://{db_path}', echo=False)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("DATABASE CREATED SUCCESSFULLY\n")


# init_db_classes--------------------------------------------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, bind=engine)
TransactionHandler = TransactionHandler(SessionLocal())
UserHandler = UserHandler(SessionLocal())
WalletHandler = WalletHandler(session=SessionLocal(), users=UserHandler)

# init_task_classes--------------------------------------------------------------------------------------------------------------
Task = Task(TransactionHandler, UserHandler, WalletHandler)
UserInterface = UserInterface(Task)

if __name__ == '__main__':
    Task.add_user()
    Task.add_start_currency_to_wallet()
    UserInterface.main_commands_handler()