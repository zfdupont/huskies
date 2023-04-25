from merge_data import merge_all
from get_neighbors import neighbors_all
def preprocess_all():
    merge_all()
    neighbors_all()
if __name__ == '__main__':
    preprocess_all()