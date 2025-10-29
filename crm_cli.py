from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date
from mimesis import Person, Datetime, Finance
from tabulate import tabulate

DATABASE_URL = "mysql+pymysql://crmuser:crm123@localhost:3306/employees_db"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    position = Column(String(50), nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    manager = relationship("Employee", remote_side=[id], backref="subordinates")

Base.metadata.create_all(engine)

person_gen = Person()
date_gen = Datetime()
finance_gen = Finance()

positions = ["CEO", "Manager", "Team Lead", "Senior Developer", "Developer"]

def generate_employee(manager_id=None):
    return Employee(
        full_name=person_gen.full_name(),
        position=positions[0] if manager_id is None else positions[1 + (manager_id % 4)],
        hire_date=date_gen.date(start=2000, end=2025),
        salary=finance_gen.price(minimum=30000, maximum=300000),
        manager_id=manager_id
    )

def add_employee():
    name = input("ФИО: ")
    position = input(f"Должность ({', '.join(positions)}): ")
    salary = float(input("Зарплата: "))
    manager_id = input("ID начальника (оставьте пустым, если нет): ")
    manager_id = int(manager_id) if manager_id else None
    emp = Employee(full_name=name, position=position, salary=salary,
                   hire_date=date.today(), manager_id=manager_id)
    session.add(emp)
    session.commit()
    print("Сотрудник добавлен!")

def list_employees():
    employees = session.query(Employee).all()
    table = []
    for emp in employees:
        manager_name = emp.manager.full_name if emp.manager else "-"
        table.append([emp.id, emp.full_name, emp.position, emp.hire_date, emp.salary, manager_name])
    print(tabulate(table, headers=["ID", "ФИО", "Должность", "Дата приема", "Зарплата", "Начальник"]))

def delete_employee():
    emp_id = int(input("ID сотрудника для удаления: "))
    emp = session.query(Employee).get(emp_id)
    if emp:
        session.delete(emp)
        session.commit()
        print("Сотрудник удален!")
    else:
        print("Сотрудник не найден!")

def update_employee():
    emp_id = int(input("ID сотрудника для изменения: "))
    emp = session.query(Employee).get(emp_id)
    if not emp:
        print("Сотрудник не найден!")
        return
    emp.full_name = input(f"ФИО ({emp.full_name}): ") or emp.full_name
    emp.position = input(f"Должность ({emp.position}): ") or emp.position
    salary = input(f"Зарплата ({emp.salary}): ")
    emp.salary = float(salary) if salary else emp.salary
    manager_id = input(f"ID начальника ({emp.manager_id}): ")
    emp.manager_id = int(manager_id) if manager_id else emp.manager_id
    session.commit()
    print("Сотрудник обновлен!")

def main_menu():
    while True:
        print("\n--- Меню ---")
        print("1. Добавить сотрудника")
        print("2. Просмотреть сотрудников")
        print("3. Изменить сотрудника")
        print("4. Удалить сотрудника")
        print("5. Выход")
        choice = input("Выберите действие: ")
        if choice == "1":
            add_employee()
        elif choice == "2":
            list_employees()
        elif choice == "3":
            update_employee()
        elif choice == "4":
            delete_employee()
        elif choice == "5":
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main_menu()
