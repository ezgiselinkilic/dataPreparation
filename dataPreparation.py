from bs4 import BeautifulSoup as soup
import requests
import pandas as pd

#Her sayfadan otomatik verileri çekmek için bir fonksiyon oluşturuldu.
def get_data(pageNo):
    my_url = 'https://www.newegg.com/p/pl?d=gaming+chairs&page='+str(pageNo)
    page_html=requests.get(my_url).content
    page_soup = soup(page_html,"html.parser")
    alls=[]
#For döngüsü içerisinde istenilen verilerin sayfadaki yerlerinden çekilerek alls dizisine aktarılması sağlandı.
    for page_soup in page_soup.findAll('div',{'class':'item-container'}):
        productBrand=page_soup.find('a',attrs={'class':'item-brand'})
        oldPrice=page_soup.find('span',{'class':'price-was-data'})
        price=page_soup.find('li',{'class':'price-current'}).find('strong')
        newPrice=page_soup.find('li',{'class':'price-current'}).find('sup')
        itemRating=page_soup.find('div',{'class':'item-branding'}).find('span',{'class':'item-rating-num'})
        savePercent=page_soup.find('li',{'class':'price-save'}).find('span',{'class':'price-save-percent'})
        all1=[]
#Gelen veriler eklenmeden önce ön işleme adımlarına uyması açısından uygun tiplere dönüştürüldü.
        if productBrand is not None:
            all1.append(productBrand.img["alt"])
        else:
            all1.append(None)

        if oldPrice is not None:
            all1.append(float(oldPrice.text[1:-1].strip()))
        else:
             all1.append(None)   
       
        if price is not None:
            newPrice=(price.text+newPrice.text)[0:-3].replace(',','.')
            all1.append(float(newPrice))
        else:
           all1.append(None)
    
        if itemRating is not None:
            all1.append(int(itemRating.text[1:-1]))
        else:
            all1.append(None)

        if savePercent is not None:
            all1.append(int(savePercent.text[0:-1]))
        else:
            all1.append(None)

        alls.append(all1)
       
    return alls

results = []
#Fonksiyondan gelen değerler results dizisine aktarıldı.
for i in range(2, 30):
    results.append(get_data(i))
    
#Resulttan gelen verilerle veri seti oluşturuldu.Veri ön işleme adımları gerçekleştirildi.

flatten = lambda l: [item for sublist in l for item in sublist]
df = pd.DataFrame(flatten(results),columns=['productBrand','oldPrice','newPrice','itemRating', 'savePercent'])
#Kategorik değişken kırılımına göre değer atama işlemi gerçekleştirildi.
#Mod alınarak hangi markanın yoğunlukta olduğu bulundu ve boş olan ürün markası verileri dolduruldu.
df['productBrand'].fillna(df["productBrand"].mode()[0],inplace=True)

#Sayısal değişkenlerden boş olanlar ise verilerin ortalaması ile dolduruldu.
df.fillna(df.mean()['oldPrice':'savePercent'],inplace=True)

#One-hot dönüşümü ile kategorik olan değerler numeric hale getirildi.
from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder(handle_unknown='ignore')
enc_df = pd.DataFrame(enc.fit_transform(df[['productBrand']]).toarray())
df = df.join(enc_df)
df.to_csv('./neweggProduct.csv', index=False, encoding='utf-8')
df=pd.read_csv('./neweggProduct.csv')
df.head()