from app import app, db
from app.models import Income_Category, Expense_Category

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        expense_categories = [
            "Kredi Ödemesi", "Borç", "Yeme - içme", "Ulaşım", "Yatırım",
            "Eğlence", "Sağlık", "Kira", "Eğitim"
        ]

        income_categories = [
            "Maaş", "Kredi", "Ödenek", "Borç geri ödeme", "Yatırım", "İş", "Diğer"
        ]

        if not Income_Category.query.first():
            for name in income_categories:
                db.session.add(Income_Category(name=name))
            db.session.commit()

        if not Expense_Category.query.first():
            for name in expense_categories:
                db.session.add(Expense_Category(name=name))
            db.session.commit()

    app.run(debug=True)
