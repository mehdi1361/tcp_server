from dal.models import User
from sqlalchemy.orm import sessionmaker


def main():
    Session = sessionmaker()
    session = Session()
    query = session.query(User)
    t = query.filter_by(username='mehdi').first()
    print('{} {}'.format(t.id, t.username))


if __name__ == '__main__':
    main()
