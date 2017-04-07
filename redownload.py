from artwork.artwork import ArtworkDataset
import os


RESULT_DATASET = "artwork_dataset_filtered.json"
OLD_DATASET_PATH="./dataset/dataset_dbpedia_3120"
NEW_DATASET_PATH="./dataset/dataset_redownload_missing"

MIN_G_IMG = 0
MIN_F_IMG = 0
MIN_S_IMG = 1



SHOW_STATS = True
SHOW_DOWNLOAD_STATS = True



DOWNLOAD = True

G_NEW_DOWN = 0
F_NEW_DOWN = 0
SEED_NEW_DOWN = True


SLEEP_BETWEEN_ARTWORK = 0.5
DBPEDIA_WIDTH = 800


def main():
    old_data = ArtworkDataset()
    old_data.loadJson(RESULT_DATASET)

    new_data = ArtworkDataset(img_path=NEW_DATASET_PATH)
    new_data = get_few_img_class_dataset(old_data, min_s_img=MIN_S_IMG, min_f_img=MIN_F_IMG, min_g_img=MIN_G_IMG, out_dataset=new_data)

    few_img_classes = len(new_data.artworks)
    if SHOW_STATS:
        print("Classes with few images: " + str(few_img_classes) )

    if DOWNLOAD:
        if G_NEW_DOWN > 0:
            new_data.downloadGoogleImages(images_per_artwork=G_NEW_DOWN, sleep_between_artwork=SLEEP_BETWEEN_ARTWORK)

        if F_NEW_DOWN > 0:
            new_data.downloadFlickrImages(api_key="flickr.apikey", images_per_artwork=F_NEW_DOWN,
                                          sleep_between_artwork=SLEEP_BETWEEN_ARTWORK)
        if SEED_NEW_DOWN:
            new_data.downloadDbPediaThumbs(preferred_dim=DBPEDIA_WIDTH, sleep_between_artwork=SLEEP_BETWEEN_ARTWORK)

        if SHOW_DOWNLOAD_STATS:
            get_few_img_class_dataset(new_data, min_s_img=MIN_S_IMG, min_f_img=MIN_F_IMG, min_g_img=MIN_G_IMG)
            print("Classes with few images before redownload: " + str(few_img_classes))
            print("Classes with few images after redownload: " + str(len(new_data.artworks)))



def get_few_img_class_dataset(dataset, min_s_img, min_g_img, min_f_img, out_dataset=ArtworkDataset()):
    # Type(ArtworkDataset, int, int, int, ArtworkDataset) -> ArtworkDataset

    for artwork in dataset.artworks:
        files = os.listdir(os.path.join(OLD_DATASET_PATH, artwork.getFolderName()))
        # if len(files) > MIN_G_IMG + MIN_F_IMG + MIN_S_IMG:
        #     continue
        gimg = 0
        fimg = 0
        seed = 0


        for f in files:
            if f.startswith("google"):
                gimg += 1
            elif f.startswith("flickr"):
                fimg += 1
            elif f.startswith("seed"):
                seed += 1
        if gimg < MIN_G_IMG or fimg < MIN_F_IMG or seed < MIN_S_IMG:
            out_dataset.artworks.append(artwork)

    return out_dataset




if __name__ == "__main__":
 main()