import codecs

from artwork.artwork import ArtworkDataset


ARTWORK_DATASET = "data/artwork_dataset_filtered_ordered.json"
OUTPUT_TXT = "data/documents.txt"
CLASS_FILTER_TXT = "data/list_of_included_classes.txt"
CLASS_NAMES_FILTER_TXT = "data/list_of_included_class_names.txt"


def main():
    doc_processing =  lambda str: str.replace('\n', '')
    filter = txt_to_list(CLASS_FILTER_TXT)
    filter = [int(f) for f in filter]
    filter_names = txt_to_list(CLASS_NAMES_FILTER_TXT)
    prepare_docs(OUTPUT_TXT, doc_processing, include_classes_filter=filter, class_filter_per_name=filter_names)

def txt_to_list(file_path, splitter='\n'):
    inf = codecs.open(file_path, 'r', encoding='utf-8')
    str = inf.read()
    inf.close()
    return str.split(splitter)




def prepare_docs(out_file, lambda_on_doc_str=None, include_classes_filter=None, class_filter_per_name=None):
    # type: (basestring, callable(basestring), list[int], list[basestring]) -> None
    ad = ArtworkDataset()
    ad.loadJson(ARTWORK_DATASET)

    outf = file(out_file, mode='w')

    for class_index, artwork in enumerate(ad.artworks):

        if include_classes_filter is not None:


            if class_index not in include_classes_filter:
                continue #skip this class!
            else:
                print(u"Included class:  " + unicode(class_index))
                i = include_classes_filter.index(class_index)
                print(u"With class name: " + unicode(class_filter_per_name[i]))
                print("")
                #ust for check:
                if class_filter_per_name is not None:
                    folder_uri = artwork.getFolderName()
                    if folder_uri != class_filter_per_name[i]:
                        raise ValueError("Wow... stop it! Probably class index not corresponding from dataset to training set?")

        title = artwork.title
        descr = artwork.description
        comment = artwork.comment
        authors = artwork.authors
        #locations = artwork.currentLocations


        if comment is None:
            comment = u''
        if descr is None:
            descr = u''
        if title is None:
            title = u''

        authors_str = u""
        if authors is not None:
            for author in authors:
                if author.name is not None:
                    authors_str += u"Author Name: " + author.name + u". "
                if author.comment is not None:
                    authors_str += author.comment + u". "
                if author.abstract is not None:
                    authors_str += author.abstract + u". "

                if author.birthDate is not None:
                    authors_str += u"Author Birth: " + str(author.birthDate)
                if author.deathDate is not None:
                    authors_str += u", Author Death: " + str(author.deathDate) + u'. '
                else:
                    authors_str += '. '

                if author.movement is not None:
                    authors_str += u"Author Movement: " + author.movement + u'. '

                if author.nationality is not None:
                    authors_str += u"Author Nationality: " + author.nationality + u'. '

        locations_str = u""
        # if locations is not None:
        #     for loc in locations:
        #         authors_str += str(loc)

        doc = title + u'. ' + authors_str + '. ' + comment + '. ' + descr +'. ' + locations_str
        # doc.replace('\n', '')
        if lambda_on_doc_str is not None:
            doc = lambda_on_doc_str(doc)
        doc += u'\n'
        outf.write(doc.encode("UTF-8"))

    outf.close()


if __name__ == "__main__":
    main()