import os
import json

from PIL import Image
import imagehash
import matplotlib.pyplot as plt

from concurrent.futures import ThreadPoolExecutor

def create_path(folder):
    """create all the picture paths under the folder"""

    img_paths = []
    try:
        path_sum = os.listdir(folder)
    except FileNotFoundError:
        return []
    # make sure no error would occur when an empty path is passed to the function
    for path in path_sum:
        if len(path.split(".")) < 2:
            img_paths = img_paths + create_path(os.path.join(folder, path))
            # search image paths thoroughly
        else:
            img_paths.append(os.path.join(folder, path))
    return img_paths

def compute_hash(img_path):
    """compute hash of an image"""

    ignored_pics = ['D:\\30242\\Pictures\\PhonePicture\\QQ\\Image_21691146758701.png']
    # pictures to ignore
    if (img_path in ignored_pics) or img_path == '':
        return None, img_path

    try:
        img = Image.open(img_path).convert('L').resize((8, 8), Image.Resampling.LANCZOS)
        return imagehash.average_hash(img), img_path
    except:
        return None, img_path

def generate_id_parallel(folder_path):
    """
    generate hash values of pictures from folder_path.
    returns lists of repeated images (updated and new) and a dictionary of current hashes
    """

    with open('stored_info\\hash.json', 'r') as f:
        hash_dict = json.load(f)
        if hash_dict:
            hash_dict = {imagehash.hex_to_hash(hash_value): value for hash_value, value in hash_dict.items()}
            # convert stored hex string into imagehash format
        old_pictures = [value for value in hash_dict.values()]
    with open('stored_info\\repeat.json', 'r') as f:
        old_rep_list = json.load(f)
    # get hash values and old repeated pictures from the current file

    img_paths = list(set(create_path(folder_path)) - set(old_pictures))
    # expel paths already in the hash table
    new_rep_list = []
    total = len(img_paths)
    count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        for img_hash, picture_path in executor.map(compute_hash, img_paths):
            if img_hash is None:
                continue

            found = False
            for h, n in hash_dict.items():
                if img_hash - h < 5:
                    found = True
                    if ([picture_path, n] not in old_rep_list) and ([n, picture_path] not in old_rep_list):
                        new_rep_list.append([picture_path, n])
                        # avoid repetition
                    break
            if not found:
                hash_dict[img_hash] = picture_path

            count += 1
            percent = count / total * 100
            if count % 100 == 0:
                print(f"Processed {count} images, progress at {percent}%")

    updated_rep_list = old_rep_list + new_rep_list
    string_hash_dict = {str(hash_dict_element): val for hash_dict_element, val in hash_dict.items()}

    return updated_rep_list,new_rep_list, string_hash_dict

def store_info(repeat_list, hash_dictionary):
    """store hash values of pictures from repeat_list"""

    with open('stored_info\\hash.json', 'w') as fp:
        json.dump(hash_dictionary, fp, indent=4)
    with open('stored_info\\repeat.json', 'w') as fp:
        json.dump(repeat_list, fp, indent=4)

def show_repeated_images(repeat_list):
    """show repeated images"""

    title_font = {'family': ["LXGW WenKai", "DejaVu Sans"]}
    # customized font
    count = 0
    for img_paths in repeat_list:
        plt.figure(figsize=(10, 15))

        for index, img_path in enumerate(img_paths):
            plt.subplot(1, 3, index * 2 + 1)
            # place the pictures at the sides of the plot block
            ax = plt.gca()

            try:
                img = Image.open(img_path)
            except:
                print(f"Error reading image {img_path}.")
                continue

            ori_size = img.size
            plt.imshow(img)
            plt.title(os.path.basename(img_path) + '\n' + str(ori_size), fontdict=title_font)
            ax.axes.xaxis.set_visible(False)
            ax.axes.yaxis.set_visible(False)

            print(os.path.basename(img_path))

        count += 1
        print(f"Repeated pair {count}")
        plt.show()