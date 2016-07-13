
class CRUD():
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

@api.route('/players/<int:id>')
def get_player(id):
    player = Player.query.get_or_404(id)
    return jsonify(player.to_json())