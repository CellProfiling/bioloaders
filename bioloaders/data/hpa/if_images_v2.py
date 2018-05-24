'A lot of this is copied from https://github.com/pytorch/vision/blob/master/torchvision/datasets/mnist.py'

from bioloaders.utils import transfer
from bioloaders.dataset import Dataset
import os
import os.path
import errno
import gzip
import glob
import numpy as np
from bioloaders.utils import utils

from tqdm import tqdm

#from scipy import misc -- depricated 
import imageio

import pdb

class hpaif(Dataset):
    
    """`HPA Cell Atlas Sample  <if.proteinatlas.org/672/672_E*>`_ Dataset.
    Args:
        root (string): Root directory of dataset where ``processed/training.pt``
            and  ``processed/test.pt`` exist.
        train (bool, optional): If True, creates dataset from ``training.pt``,
            otherwise from ``test.pt``.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.
        transform (callable, optional): A function/transform that  takes in a Y,X,C image
            and returns a transformed version.
        label_type (string, optional): {'onehot', 'index', 'string'} specifies the output 
            type of the label.
    """
    
  
    info = ['if.proteinatlas.org/672/672_E2*','https://github.com/CellProfiling',
             """@article {thul2017subcell, \
             author={Peter J Thul, Lovisa Akesson, et al.}, \
             title = {A subcellular map of the human proteome}, \
             year = {2017}, \
             url={http://science.sciencemag.org/content/early/2017/05/10/science.aal3321}, \
             journal={Science}, \
             }"""]
    
    def __init__(self, root, train=False, transform=None, 
                 username=None, password=None, buffer_images=True,
                 download=False,dest='./',acc_list=None,force_download=False):
        self.remote = 'https://if.proteinatlas.org'
        self.root = os.path.expanduser(root)
        self.transform = transform
        #self.train = train
        self.buffer_images = buffer_images
        self.username = username
        self.password = password
        self.dest = dest
        self.files = acc_list 
        print(self.files)
            
        if not self._check_exists() or force_download:
            if download or force_download:
                self.download()
            else:
                raise RuntimeError('Dataset not found.' +
                               ' You can use download=True to download it')
        

        image_paths = glob.glob(os.path.join(self.dest, '*.tif.gz'))
        imgnames = [path.split(os.path.sep)[-1] for path in image_paths]
        plates = []
        wells = []
        fields = []
        plate_wells = []
        name_list = []
        for name in imgnames:
           print(name)
           name_parts = name.split('_')
           plates.append(name_parts[0])
           wells.append(name_parts[1])
           fields.append(name_parts[2])
           plate_wells.append('_'.join([plates[-1],wells[-1]]))
           name_list.append(name)
           print(plate_wells[-1])
        uplate_wells, plate_wells_index = np.unique(plate_wells, return_inverse=True)
        
        self.labels = plate_wells
        self.ulabels = uplate_wells
        self.plates = plates
        self.wells = wells
        self.fields = fields
        self.name_list = name_list
        
        self.image_paths = image_paths
        
        if buffer_images:
            print('Buffering images')
            self.images = [imageio.imread(path) for path in tqdm(image_paths)]
        else:
            print('not buffering')
                
        
        
        
        
    def __getitem__(self, index):
        if self.buffer_images:
            image = self.images[index]
        else:
            print(self.image_paths[index])
            with gzip.open(self.image_paths[index],'rb') as img:
                print('reading image')
                print(self.image_paths[index])
                image = imageio.imread(img)
            
            
        return {'image': image, 'label': self.name_list[index]}
    
    def __len__(self):
        return len(self.image_paths)
    
    def _check_exists(self):
        #this could be done better
               
        return os.path.exists(self.dest)

    
    def download(self):
        """Download the data if it doesn't exist in processed_folder already."""
    
        if self._check_exists():
                return   
        try:
            os.makedirs(self.root)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise
        transfer.download(self.remote,self.dest,self.files,self.username,self.password)
        '''for url in self.urls:
            print('Downloading ' + url)
            data = urllib.request.urlopen(url)
            filename = url.rpartition('/')[2]
            file_path = os.path.join(self.root, filename)
            with open(file_path, 'wb') as f:
                f.write(data.read())
                
            with tarfile.open(file_path) as zip_f:
                zip_f.extractall(path=self.root)
            os.unlink(file_path)'''
            
        print('Done!')
    
        pass
    
