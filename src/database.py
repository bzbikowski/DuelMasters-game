from PySide2.QtSql import QSqlDatabase, QSqlQuery

from src.cards import ParseXml


class Database(object):
    def __init__(self):
        # todo cleanup class and add doc
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("dataset.db")
        # db.setUserName(os.getenv("DB_LOG"))
        # db.setPassword(os.getenv("DB_PASS"))
        if not self.db.open():
            print(self.db.lastError())
            return
        if not self.check_if_initialized():
            ds_querry = QSqlQuery(self.db)
            ok = ds_querry.exec_("CREATE TABLE dataset(id integer primary key autoincrement, name text);")
            if not ok:
                print(ds_querry.lastError())
            cd_querry = QSqlQuery(self.db)
            q = """CREATE TABLE card(id integer not null primary key autoincrement, name varchar(50), civilization varchar(10), type varchar(10),
                               race varchar(30), cost int, power int, rarity varchar(5), collector_number varchar(5),
                               artist varchar(50), rules text, flavor text, effects json_text, high_res blob,
                               low_res blob, cardset int, foreign key (cardset) references dataset(id));"""
            ok = cd_querry.exec_(q)
            if not ok:
                print(cd_querry.lastError())
            for card in ParseXml().parseFile("res//cards.xml"):
                querry = QSqlQuery(self.db)
                q = "INSERT INTO card (name, civilization, type, race, cost, power, rarity, collector_number, artist," \
                    " rules, flavor, effects, high_res, low_res, cardset) values (:name, :civ, :type, :race, :cost," \
                    " :power, :rarity, :col_num, :artist, :rules, :flavor, :effects, :high, :low," \
                    " (SELECT id FROM dataset WHERE name == :set_name));"
                querry.prepare(q)
                querry.bindValue(":name", card.name)
                querry.bindValue(":civ", card.civ)
                querry.bindValue(":type", card.typ)
                querry.bindValue(":race", card.race)
                querry.bindValue(":cost", int(card.cost))
                querry.bindValue(":power", int(card.power))
                querry.bindValue(":rarity", card.rarity)
                querry.bindValue(":col_num", card.col_num)
                querry.bindValue(":artist", card.artist)
                querry.bindValue(":rules", card.rules_text)
                querry.bindValue(":flavor", card.flavor_text)
                querry.bindValue(":effects", card.effects_json)
                querry.bindValue(":high", card.images['high'])
                querry.bindValue(":low", card.images['low'])
                querry.bindValue(":set_name", card.set_name)
                ok = querry.exec_()
                if not ok:
                    print(f"DLA {card.name}: {querry.lastError().text()}")
                    return

    def check_if_initialized(self):
        querry = QSqlQuery(self.db)
        ok = querry.exec_(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND (name='card' OR name='dataset');")
        if not ok:
            print(querry.lastError())
        querry.next()
        if not querry.value(0) == 0:
            return True
        return False

    def count(self):
        querry = QSqlQuery(self.db)
        ok = querry.exec_(
            "SELECT count(name) FROM card;")
        if not ok:
            print(querry.lastError())
        querry.next()
        return querry.value(0)

    def getdata(self, id, atr):
        querry = QSqlQuery(self.db)
        querry.prepare(f"SELECT {atr} FROM card WHERE id==:id;")
        querry.bindValue(":id", id + 1)
        ok = querry.exec_()
        if not ok:
            print(querry.lastError())
        querry.next()
        data = querry.value(0)
        return data
