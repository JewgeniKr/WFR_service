from app import db

class ImageType(db.Model):
    __tablename__ = 'images_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    # Связь: один ImageType имеет много Image
    images = db.relationship('Image', backref='type', lazy=True,
                             cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ImageType {self.name}>'

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(500))

    # ВНЕШНИЙ КЛЮЧ к таблице image_types
    image_type_id = db.Column(db.Integer,
                              db.ForeignKey('images_types.id', ondelete='CASCADE'),
                              nullable=False,
                              index=True)  # индекс для быстрого поиска

    def __repr__(self):
        return f'<Image {self.name}>'

class MLModelType(db.Model):
    __tablename__ = 'ml_models_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    # Связь: один MLModelType имеет много MLModel
    images = db.relationship('MLModel', backref='type', lazy=True,
                             cascade='all, delete-orphan')

class MLModel(db.Model):
    __tablename__ = 'ml_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(500))

    # ВНЕШНИЙ КЛЮЧ к таблице ml_models_types
    ml_model_type_id = db.Column(db.Integer,
                              db.ForeignKey('ml_models_types.id', ondelete='CASCADE'),
                              nullable=False,
                              index=True)  # индекс для быстрого поиска
