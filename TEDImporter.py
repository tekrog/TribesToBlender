from .terrain import terrain
def load_ted(filename):
    ter = terrain.terrain()
    ter.load_file(filename)
    ter.print_stats()