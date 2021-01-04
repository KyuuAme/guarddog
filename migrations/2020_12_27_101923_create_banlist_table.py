from orator.migrations import Migration


class CreateBanlistTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('banlist') as table:
            table.increments('id')
            table.big_integer('user_id')
            table.big_integer('banned_by')
            table.text('reason')
            table.integer('banned_on').unsigned()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('banlist')
