import json
import os
import logging
from PySide6.QtCore import QObject, QFile, QIODevice, QStandardPaths, QThread, Signal
from PySide6.QtSql import QSqlDatabase, QSqlQuery


from src.cards import Card


class Database(QObject):
    finished_inicialization = Signal(None)
    def __init__(self):
        super(Database, self).__init__()
        # TODO: proper gid and sid logic
        self.db = QSqlDatabase.addDatabase("QSQLITE")

        # set db location to $HOME/.local/share/
        if not os.path.exists(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)):
            os.mkdir(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        self.db.setDatabaseName(os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation), "dataset.db"))

    def initialize_database(self):
        # TODO: make this function not blocking
        res_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "res")
        if not self.db.open():
            logging.error(self.db.lastError())
            return
        if not self.check_if_initialized():
            ds_querry = QSqlQuery(self.db)
            ds_ok = ds_querry.exec_("CREATE TABLE dataset(id integer primary key, name text);")
            if not ds_ok:
                logging.error(ds_querry.lastError().text())
                return
            as_querry = QSqlQuery(self.db)
            as_ok = as_querry.exec_("CREATE TABLE asset(id integer primary key, name text, image blob);")
            if not as_ok:
                logging.error(as_querry.lastError().text())
                return
            
            images_res_path = os.path.join(res_path, "img")
            assets = [("cardback", f"{images_res_path}//cardback.png"), ("background", f"{images_res_path}//background.png"), ("preview", f"{images_res_path}//console.png"), ("lock", f"{images_res_path}//lock.png")]
            for asset_name, asset_path in assets:
                file = QFile(asset_path)
                if not file.open(QIODevice.ReadOnly):
                    logging.error(f"ERROR: couldn't open file {asset_path}")
                    return
                image_blob = file.readAll()
                as_querry_init = QSqlQuery(self.db)
                q = "INSERT INTO asset(name, image) VALUES (:name, :image);"
                as_querry_init.prepare(q)
                as_querry_init.bindValue(":name", asset_name)
                as_querry_init.bindValue(":image", image_blob)
                as_ok_init = as_querry_init.exec_()
                if not as_ok_init:
                    logging.error(f"ASSET INIT SQL ERROR: asset {asset_name}: {as_querry_init.lastError().text()}")
                    return
            cd_querry = QSqlQuery(self.db)
            q = """CREATE TABLE card(id integer primary key, sid int, gid int, name varchar(50), civilization varchar(10), type varchar(10),
                               race varchar(30), cost int, power int, rarity varchar(5), collector_number varchar(5),
                               artist varchar(50), rules text, flavor text, effects json_text, high_res blob, medium_res blob,
                               low_res blob, cardset int, foreign key (cardset) references dataset(id));"""
            cd_ok = cd_querry.exec_(q)
            if not cd_ok:
                logging.error(cd_querry.lastError().text())
                return
            for id, global_id, setname, cardname, civ, card_type, race, cost, power, rarity, col_num, artist, rule_text, flavor_text, raw_effects in Card.parseFile(f"{res_path}//cards.xml"):
                images = Card.load_images(images_res_path, setname, id)
                _, effects_string = Card.parse_effects(raw_effects)
                querry = QSqlQuery(self.db)
                q = "INSERT INTO card (sid, gid, name, civilization, type, race, cost, power, rarity, collector_number, artist," \
                    " rules, flavor, effects, high_res, medium_res, low_res, cardset) values (:sid, :gid, :name, :civ, :type, :race, :cost," \
                    " :power, :rarity, :col_num, :artist, :rules, :flavor, :effects, :high, :medium, :low," \
                    " (SELECT id FROM dataset WHERE name == :set_name));"
                querry.prepare(q)
                querry.bindValue(":sid", id)
                querry.bindValue(":gid", global_id)
                querry.bindValue(":name", cardname)
                querry.bindValue(":civ", civ)
                querry.bindValue(":type", card_type)
                querry.bindValue(":race", race)
                querry.bindValue(":cost", int(cost))
                querry.bindValue(":power", int(power))
                querry.bindValue(":rarity", rarity)
                querry.bindValue(":col_num", col_num)
                querry.bindValue(":artist", artist)
                querry.bindValue(":rules", rule_text)
                querry.bindValue(":flavor", flavor_text)
                querry.bindValue(":effects", effects_string)
                querry.bindValue(":high", images['high'])
                querry.bindValue(":medium", images['medium'])
                querry.bindValue(":low", images['low'])
                querry.bindValue(":set_name", setname)
                ok = querry.exec_()
                if not ok:
                    logging.error(f"CARD INIT SQL ERROR: card {cardname}: {querry.lastError().text()}")
                    return
        self.finished_inicialization.emit()

    def check_if_initialized(self):
        querry = QSqlQuery(self.db)
        ok = querry.exec_(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND (name='card' OR name='dataset' OR name='asset');")
        if not ok:
            logging.error(querry.lastError().text())
        querry.next()
        if not querry.value(0) == 0:
            return True
        return False

    def count(self):
        querry = QSqlQuery(self.db)
        ok = querry.exec_(
            "SELECT count(name) FROM card;")
        if not ok:
            logging.error(querry.lastError().text())
        querry.next()
        return querry.value(0)

    def get_data(self, id, atr):
        querry = QSqlQuery(self.db)
        querry.prepare(f"SELECT {atr} FROM card WHERE sid==:sid;")
        querry.bindValue(":sid", id)
        ok = querry.exec_()
        if not ok:
            logging.error(querry.lastError().text())
            return
        querry.next()
        data = querry.value(0)
        return data

    def get_card(self, id):
        querry = QSqlQuery(self.db)
        querry.prepare(f"SELECT sid, gid, name, civilization, type, race, cost, power, effects, cardset FROM card WHERE sid==:sid;")
        querry.bindValue(":sid", id)
        ok = querry.exec_()
        if not ok:
            logging.error(querry.lastError().text())
            return
        querry.next()
        sid = querry.value(0)
        gid = querry.value(1)
        name = querry.value(2)
        civ = querry.value(3)
        type = querry.value(4)
        race = querry.value(5)
        cost = querry.value(6)
        power = querry.value(7)
        effect_string = querry.value(8)
        cardset = querry.value(9)
        return Card(sid, gid, name, civ, type, race, cost, power, json.loads(effect_string)["effects"], cardset)

    def get_asset(self, name):
        querry = QSqlQuery(self.db)
        querry.prepare(f"SELECT image FROM asset WHERE name==:name;")
        querry.bindValue(":name", name)
        ok = querry.exec_()
        if not ok:
            logging.error(querry.lastError().text())
            return
        querry.next()
        image = querry.value(0)
        return image