import copy
import codecs
from artwork.artwork import ArtworkDataset


DATASET_PATH = "./dataset/dataset_new/"
UNORDERED_DATASET = "data/artwork_dataset_filtered.json"
ORDERED_DATASET = "data/artwork_dataset_filtered_ordered.json"

CLASS_NAME_ORDERING_FILE="data/dbp3120_class_order.txt"


def main():
    artwork_dataset_ordering(class_name_ordered_file=CLASS_NAME_ORDERING_FILE, unordered_dataset_path=UNORDERED_DATASET,
                             ordered_dataset_out_path=ORDERED_DATASET)



def artwork_dataset_ordering(class_name_ordered_file, unordered_dataset_path, ordered_dataset_out_path=None):
    ordering = txt_to_list(class_name_ordered_file)
    not_ordered_dataset = ArtworkDataset().loadJson(unordered_dataset_path)

    ordered_artwork_dict = {}
    for artwork in not_ordered_dataset.artworks:
        try:
            index = ordering.index(artwork.getFolderName())
        except ValueError as v:
            print "Artwork not find in the ordering list"
            raise v
        ordered_artwork_dict[index] = artwork

    ordered_dataset = copy.deepcopy(not_ordered_dataset)
    ordered_dataset._artworks = ordered_artwork_dict.values()
    if ordered_dataset_out_path is not None:
        ordered_dataset.saveJson(ordered_dataset_out_path)
    return ordered_dataset


def txt_to_list(file_path, splitter='\n'):
    inf = codecs.open(file_path, 'r', encoding='utf-8')
    str = inf.read()
    inf.close()
    return str.split(splitter)



if __name__ == "__main__":
    main()