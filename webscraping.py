#this code was used in a DRF function based view
import requests
import time
from bs4 import BeautifulSoup
def lancerwebscraping(request):
    scrapingtime=int(request.data['scrapingtime'])
    scrapingtime=scrapingtime // 2
    pagecpt=1
    #for scraping all pages
    while pagecpt <= scrapingtime:
        if pagecpt==1:
            page=requests.get("http://www.annonce-algerie.com/AnnoncesImmobilier.asp").text
        else:
            page=requests.get(f"http://www.annonce-algerie.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=&rech_cod_typ=&rech_cod_sou_typ=&rech_cod_pay=DZ&rech_cod_reg=&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31&rech_page_num={pagecpt}").text
        time.sleep(5)
        soup=BeautifulSoup(page,'lxml')
        anchors=soup.find_all('a')
        #get all links for the posts in the real estate posts table
        for anchor  in anchors :
            #cleaning data to use it with my model to save in the database
            lien=anchor["href"]
            if "cod_ann" in lien:
                pagedetail=requests.get(f"http://www.annonce-algerie.com/{lien}").text
                time.sleep(5)
                soupdetail=BeautifulSoup(pagedetail,'lxml')
                params=soupdetail.find_all('td',class_='da_field_text')
                datalist=[]
                for param in params:
                    data=param.text
                    datalist.append(data.replace("\xa0","").replace("\r","").replace("\n","").replace("\t",""))
                check=soupdetail.find(id='all_photos')
                if check:
                    divs=soupdetail.find(id='all_photos').find_all('a')
                    for anchor in divs:
                        img=anchor["href"].replace("javascript:photo_apercu('","")
                        datalist.append(img)
                soupcontact=BeautifulSoup(pagedetail,'lxml')
                contact=soupcontact.find("span",class_="da_contact_value")
                datalist.append(contact.text)
                cpt=0
                catettypeann=datalist[cpt][8:]
                categorie=catettypeann[:catettypeann.find(">")]
                typeann=catettypeann[len(categorie)+1:]
                cpt=cpt+1
                wilayacomm=datalist[cpt][9:]
                wilaya=wilayacomm[:wilayacomm.find(">")]
                commad=wilayacomm[len(wilaya)+1:]
                comm=commad[:commad.find(">")]
                cpt=cpt+1
                if not datalist[cpt][:datalist[cpt].find("m")].replace(" ","").isnumeric():
                    cpt=cpt+1
                surface=datalist[cpt][:datalist[cpt].find("m")]
                cpt=cpt+1
                prix=datalist[cpt][:datalist[cpt].find("D")]
                cpt=cpt+1
                description=datalist[cpt]
                cpt=cpt+2
                date=datalist[cpt].replace("/","-")
                correctdate=datetime.datetime.strptime(date[6:]+"-"+date[3:5]+"-"+date[:2], '%Y-%m-%d').date()
                cpt=cpt+1
                imagelist=[]
                for item in datalist[cpt:]:
                    if "upload" in item:
                        imagelist.append(item[:item.find("'")])
                        cpt=cpt+1
                telephone=datalist[cpt]
                titre=categorie+" "+typeann+" "+wilaya+" "+comm
                instance=Utilisateur.objects.get(id=43)
                annonce=Annonce.objects.create(utilisateur= instance, titre=titre,
                categorie=categorie,type=typeann,
                surface=surface,description=description or None,
                prix=prix,annonceuremail="annonce-algerie",date=correctdate)
                Contact.objects.create(annonce=annonce,telephone=telephone)
                Localisation.objects.create(annonce=annonce,wilaya=wilaya,
                commune=comm)
                for value in imagelist:                
                        Image.objects.create(lien=value,annonce=annonce)
        #go to the next page
        pagecpt=pagecpt+1
    return Response("finished")
