from app import app, db
from app.config import ProductionConfig
from services.page_validation import PageClassificator

# Для разработки
app.config.from_object(ProductionConfig)

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
