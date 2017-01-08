
class OPRouter(object):
    """
    A router to control all database operations with oddsportal
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'oddsportal':
            return 'cache_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'oddsportal':
            return 'cache_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'oddsportal' or \
           obj2._meta.app_label == 'oddsportal':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'oddsportal':
            return db == 'cache_db'
        return None

class PrimaryRouter(object):
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'oddsportal':
            return False
        return True