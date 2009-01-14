#coding=utf-8
#!/usr/bin/env python
#
#    Copyright (C) 2008 Sylvain
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import wsgiref.handlers
import logging, os, re
import random, string, cgi
import config
import paginator
import random
import base64
import urllib
import friendfeed
from sgmllib import SGMLParser
import feedparser
        
import gdata.photos.service
import gdata.alt.appengine

from google.appengine.ext import search
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api import urlfetch

class BaseIndex(db.Model):
    index = db.IntegerProperty(default=0)
    count = db.IntegerProperty(default=0)


class Image(search.SearchableModel):
    name = db.StringProperty()
    type = db.StringProperty()
    ext = db.StringProperty()
    caption = db.StringProperty(multiline=True)
    category = db.StringProperty()
    note = db.StringProperty(multiline=True)
    olink = db.StringProperty()
    opagelink = db.StringProperty()
    opagetitle = db.StringProperty(multiline=True)
    owner = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    country = db.StringProperty()
    hits = db.IntegerProperty(default=0)
    original = db.BlobProperty()
    thumbnail = db.BlobProperty()
    ext_thumb = db.StringProperty()
    length = db.IntegerProperty()
    index = db.IntegerProperty(default=0)
    uindex = db.IntegerProperty(default=0)
    shared = db.IntegerProperty(default=0)
    server = db.StringProperty(default="images")

class IMGLister(SGMLParser):
    def reset(self):                              
        SGMLParser.reset(self)
        self.urls = []
    def start_img(self, attrs):                     
            src = [v for k, v in attrs if k=='src'] 
            if src:
                self.urls.extend(src)


def ImgCol(images):
    imagescol=[]
    imagescoll=[]    
    for i in range(0,4):
      for j in range(0,5):
        if len(images)<i*5+j+1:
            img=get_image('agR5NDR5cgwLEgVJbWFnZRiHAgw')
            imagescol.append(img)
        else:
            imagescol.append(images[i*5+j])
      imagescoll.append(imagescol)
      imagescol=[] 
    return imagescoll

def GetContry(handler):
    ip = str(handler.request.remote_addr)
    url = "http://geoip.wtanaka.com/cc/"+ip
    result = urlfetch.fetch(url)
    return result.content

def publishfanfou(status):
    status = status.encode('utf-8','ignore')
    url = "http://api.fanfou.com/statuses/update.json"
    pair = "%s:%s" % ('kangk4@gmail.com','1988315')
    token = base64.b64encode(pair)
    au="Basic %s" % token
    form_data = urllib.urlencode({'status':status})
    result=urlfetch.fetch(url=url,payload=form_data,\
                                          method=urlfetch.POST,\
                                          headers={'Authorization':au})
    

    


class MainPage(webapp.RequestHandler):
    def post(self):
        
        template_values = None
        host = self.request.host_url
        file_name = ''
        img_key = ''
        error = ''
        file_content_type = ''
        ext_thumbnail = ''
        ext_original = ''
        img = None
        indexnext = 40
        sign_url, sign, user_name, user, user_is_admin = get_user_info()
        
        template_values = {
            'user_name': user_name,
            'user_is_admin': user_is_admin, 
            'sign': sign,
            'sign_url': sign_url,
            'img': img,
            'host': host,
            'setting': True,
            'error': error,
            'next': indexnext
            }
                    
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path,template_values))
    
    get = post

class Home(webapp.RequestHandler):
    def get(self):
        country = GetContry(self)
        if self.request.get("hl"):
            country = self.request.get("hl")
        if country=="cn":
            templatename="cnhome.html"
            version = self.request.path+"?hl=en"
            vername = "English"
            hl = "?hl=cn"
        else:
            templatename="home.html"
            version = self.request.path+"?hl=cn"
            vername = "中文版"
            hl = "?hl=en"
        template_values = None
        host = self.request.host_url 
        error = ''  
        sign_url, sign, user_name, user, user_is_admin = get_user_info()     
        query = db.Query(Image)
        query = Image.all()
        query.order('-date')
        #images = memcache.get('topimages')
        #if images is None:
        images = query.fetch(limit=40)
        #    if not memcache.add('topimages',images, 60):
        #        logging.error("Memcache set failed.")
        
        
#        imagescol=[]
#        imagescoll=[]
#        for i in range(0,4):
#            for j in range(0,5):
#                imagescol.append(images[i*5+j])
#            imagescoll.append(imagescol)
#            imagescol=[] 
        # imagescoll=ImgCol(images)
        template_values = {
                    'user_name': user_name,
                    'user_is_admin': user_is_admin, 
                    'sign': sign,
                    'sign_url': sign_url,
                    'images': images,
                    'host': host,
                    'setting': True,
                    'error': error,
                    'next': '/start/40'+hl,
                    'version': version,
                    'vername': vername
                    }
                            
        path = os.path.join(os.path.dirname(__file__), templatename)
        self.response.out.write(template.render(path,template_values))

class Sitemap(webapp.RequestHandler):
    def get(self):
        query = db.Query(Image)
        query = Image.all()
        query.order('-date')
        images = query.fetch(30)
        template_values = {'images': images}
        path = os.path.join(os.path.dirname(__file__), 'map.html')
        self.response.out.write(template.render(path,template_values))
    post = get

class RSS(webapp.RequestHandler):
    def get(self):
        query = db.Query(Image)
        query = Image.all()
        query.order('-date')
        images = query.fetch(40)
        template_values = {'images': images}
        path = os.path.join(os.path.dirname(__file__), 'feed.html')
        self.response.out.write(template.render(path,template_values))
    post = get

        
        
class MyPic(webapp.RequestHandler):
    def get(self):
        country = GetContry(self)
        if self.request.get("hl"):
            country = self.request.get("hl")
        if country=="cn":
            hl="?hl=cn"
            templatename="cnhome.html"
            version = self.request.path+"?hl=en"
            vername = "English"
        else:
            templatename="home.html"
            hl="?hl=en"
            version = self.request.path+"?hl=cn"
            vername = "中文版"
        
        
        template_values = None
        host = self.request.host_url 
        error = ''  
        sign_url, sign, user_name, user, user_is_admin = get_user_info()  
        if user:
             query = db.Query(Image)
             query = Image.all()
             query.filter("owner =",user)
             query.order('-date')
             images = query.fetch(limit=40)
     #        imagescol=[]
     #        imagescoll=[]
     #        for i in range(0,4):
     #            for j in range(0,5):
     #                imagescol.append(images[i*5+j])
     #            imagescoll.append(imagescol)
     #            imagescol=[] 
             # imagescoll=ImgCol(images)
             template_values = {
                         'user_name': user_name,
                         'user_is_admin': user_is_admin, 
                         'sign': sign,
                         'sign_url': sign_url,
                         'images': images,
                         'host': host,
                         'setting': True,
                         'error': error,
                         'next': '/u/40'+hl,
                         'version': version,
                         'vername': vername
                         }
                                 
             path = os.path.join(os.path.dirname(__file__), templatename)
             self.response.out.write(template.render(path,template_values))
             
        else:
             self.redirect(users.create_login_url(self.request.uri))
            
           
        

    
class GetImage(webapp.RequestHandler):
    def get(self, size, key):
        try:          
            
            img = get_image(key)
            
            if not img:
                return                
            
            #logging.info('Image requested : size = %s / %s / %s' % (size, key, img.name))

            if size == 'images':
                logging.debug('GetImage : size = %s , key = %s' % (size, key))
                data = img.original
                img.hits += 1
                img.put()
                
            elif size == 'thumbs':
                data = img.thumbnail

            

            self.response.headers['Content-Type'] = str(img.type)
            self.response.out.write(data)
            
        except Exception, e:
            logging.exception(e)
    
class Search(webapp.RequestHandler):
    def get(self):
        country = GetContry(self)
        if self.request.get("hl"):
            country = self.request.get("hl")
        if country=="cn":
            templatename="cnhome.html"
            version = "/?hl=en"
            vername = "English"
        else:
            templatename="home.html"
            version = "/?hl=cn"
            vername = "中文版"
        

        template_values = None
        host = self.request.host_url 
        error = ''  
        sign_url, sign, user_name, user, user_is_admin = get_user_info() 
        
        keyword = self.request.get('q')
        keyword = keyword#.decode('utf-8','ignore')
        #self.response.headers['Content-Type'] = 'text/html'
        if not keyword:
          self.redirect('/')
          #self.response.out.write("No keyword has been set")
        else:            
          # Search the 'Person' Entity based on our keyword
          query = Image.all().search(keyword)
          
          #for result in query.Run():
          #   self.response.out.write('%s' % result['owner'])
          #query.order('-date')
          images = query.fetch(40)
          #imagescoll = ImgCol(images) 
          
          template_values = {
                              'user_name': user_name,
                              'user_is_admin': user_is_admin, 
                              'sign': sign,
                              'sign_url': sign_url,
                              'images': images,
                              'host': host,
                              'setting': True,
                              'error': error,
                              'version':version,
                              'vername':vername
                              }
                                      
          path = os.path.join(os.path.dirname(__file__), templatename)
          self.response.out.write(template.render(path,template_values))
    post = get
          
        
            

class Detail(webapp.RequestHandler):
    def get(self, key):
        try:
            template_values = None
            host = self.request.host_url
            error = ''
            sign_url, sign, user_name, user, user_is_admin = get_user_info()
            
            logging.debug('Detail : key = %s' % (key))
            
            img = memcache.get(key)
            if img is None:
                img = get_image(key)
#                img_key = str(img.key())                                    
#                #memcache.set(img_key,img)
#                if not memcache.add(img_key,img, 60):
#                      logging.error("Memcache set failed.")
                
                        
            if not img:
                return               
            logging.info('Image Detail requested : %s / %s' % (key, img.name))
        except Exception, e:
            logging.exception(e)
            #error = 'Image error processing'
        
            
        if img.owner:
            By = img.owner.nickname()
        else:
            By = None
        if img.category:
            logging.debug("get_random_pic_by_category")
            randomimages = get_random_pic_by_category(img.category,5)
        else:
            logging.debug("get_random_pic")
            randomimages = get_random_pic(5)
        
        #randomimages = get_random_pic(5)
        country = GetContry(self)
        if self.request.get("hl"):
            country = self.request.get("hl")
        if country=="cn":
            templatename="cndetail.html"
            version = "/?hl=en"
            vername = "English"
        else:
            templatename="detail.html"
            version = "/?hl=cn"
            vername = "中文版"
        
        
        template_values = {
                               'user_name': user_name,
                               'user_is_admin': user_is_admin, 
                               'sign': sign,
                               'sign_url': sign_url,
                               'img': img,
                               'By':By,
                               'host': host,
                               'error': error,
                               'date':img.date.isoformat(' ')[0:19],
                               'random':randomimages,
                               'version':version,
                               'vername':vername
                               }
           
        path = os.path.join(os.path.dirname(__file__), templatename)
        self.response.out.write(template.render(path,template_values))
                   
            
        
        

class Error404(webapp.RequestHandler):
    def get(self, key):
        self.error(404)
        self.redirect('/')
           

class Gallery(webapp.RequestHandler):
    def get(self):
        
        img = Image.all()
        img.order('-date')

        template_values = {
                    'images': img
                    }
        
        path = os.path.join(os.path.dirname(__file__), 'gallery.xml')
        self.response.out.write(template.render(path,template_values))
        
    post=get
        
class SaveCap(webapp.RequestHandler):
    def post(self):
        key = self.request.get('key')
        caption = self.request.get('caption')
        img = get_image(key)
        img.caption=caption
        img.put()
        self.response.out.write(caption)
    get = post

class Submit(webapp.RequestHandler):    
    def post(self):
        template_values = None
        host = self.request.host_url
        file_name = ''
        error = ''
        file_content_type = ''
        ext_thumbnail = ''
        ext_original = ''
                
        sign_url, sign, user_name, user, user_is_admin = get_user_info()
        
        img = None
        
        olink = self.request.POST.get('olink')
        logging.info('Submit Image : %s' % olink)
        q = Image.all()
        q.filter("olink =",olink)
        if q.count()>0:
            img = q.fetch(limit = 1)[0]
            img.shared += 1
            img.put()
            self.response.out.write("OK")
        else:
            try:
#                result = urlfetch.fetch(olink)   
#                file_data = result.content
#                image_length = len(file_data)
#                
#                if image_length > config.max_size:
#                    error = 'File is too large'
                m=re.match("http://[^/]+/([^.]+)\.([^?]+)?.*", olink)
                #groups = m.groups()
                if m == None:
                    file_content_type = 'jpg'
                    file_name = 'image'
                else: 
                    groups = m.groups()                   
                    file_content_type = groups[1]
                    file_name = groups[0]
                caption = self.request.POST.get('caption')                
                opagetitle = self.request.POST.get('opagetitle')
                opagelink = self.request.POST.get('opagelink')
                category = self.request.POST.get('category')
                
                
                #ext_original, ext_thumbnail, o_encoding  = get_myimage_extension(file_content_type)
                ext_original, ext_thumbnail, o_encoding  = get_myimage_extension("jpg")
                img = Image()
                img.name = file_name
#                        img.original = db.Blob(images.resize(file_data, 400,
#                                                              400,
#                                                              output_encoding=o_encoding)
#)
#                        img.thumbnail = db.Blob(images.resize(file_data, config.thumbnail_size['width'],
#                                                              config.thumbnail_size['height'],
#                                                              output_encoding=o_encoding))
                img.type = file_content_type
                img.ext = ext_original
                img.owner = user
                img.caption = caption
                img.olink = olink
                img.opagelink = opagelink
                img.opagetitle = opagetitle
                #img.length = image_length
                img.ext_thumb = ext_thumbnail
                ip = str(self.request.remote_addr)
                url = "http://geoip.wtanaka.com/cc/"+ip
                result = urlfetch.fetch(url)
                img.country =result.content
                img.category = category
                rannum=random.randint(1, 10)
                img.server = "imageserver%d" % rannum
                img.put()
                img_key = str(img.key())
                
                logging.info('Random : %d' % rannum)
                if request_to_server(rannum,olink,img_key)=='OK':                 
                    
                    
                    #img.put()                  
                    ImageIndex = BaseIndex.get_by_key_name("Image")
                    if ImageIndex:
                        img.parent = ImageIndex
                        img.index = ImageIndex.index
                        #img.put()
                        ImageIndex.index += 1
                        ImageIndex.count += 1
                        ImageIndex.put()
                    else:
                        ImageIndex = BaseIndex(key_name='Image')
                        img.parent = ImageIndex
                        img.index = ImageIndex.index
                        #img.put()
                        ImageIndex.index += 1
                        ImageIndex.count += 1
                        ImageIndex.put()
                    CategoryIndex = BaseIndex.get_by_key_name("Category:"+category)
                    if CategoryIndex:
                        CategoryIndex.index += 1
                        CategoryIndex.count += 1
                        CategoryIndex.put()
                    else:
                        CategoryIndex = BaseIndex(key_name=("Category:"+category))
                        CategoryIndex.index += 1
                        CategoryIndex.count += 1 
                        CategoryIndex.put()                           
                    if user:
                        UserIndex = BaseIndex.get_by_key_name(user_name)
                        if UserIndex:
                            img.uindex = UserIndex.index
                            UserIndex.index += 1
                            UserIndex.count += 1
                            UserIndex.put()
                            img.put()
                        else:
                            UserIndex = BaseIndex(key_name=user_name)
                            img.uindex = UserIndex.index
                            UserIndex.index += 1
                            UserIndex.count += 1
                            UserIndex.put()
                            img.put()    
                    session = friendfeed.FriendFeed('dwimages','mill872calks')
                    entry = session.publish_link(
                                title=caption.encode('utf-8','ignore'),
                                link="http://images.kangye.org/imgdetail/%s" % img_key ,
                                image_urls=[
                                    "http://imageserver%d.appspot.com/images/%s%s" % (rannum,img_key,ext_thumbnail),
                                ],room="persian-cam"
                            )
                    publishfanfou((caption+"  "+"http://images.kangye.org/imgdetail/"+img_key))
                    
                else:
                    logging.info("Image from %s was failed to download." % olink)
                    img.delete()
                        
                        
                                           
                    
                    
                    memcache.set(img_key,img)

                    #publishfanfou("%s  http://images.kangye.org/imgdetail/%s" % (caption,img_key))
                    
                    #self.redirect(opagelink)
                    self.response.out.write('OK')
            except Exception, e:
                logging.exception(e)
        
        
#        template_values = {
#                            'user_name': user_name,
#                            'user_is_admin': user_is_admin, 
#                            'sign': sign,
#                            'sign_url': sign_url,
#                            'img': img,
#                            #'images': all,
#                            'host': host,
#                            'error': error,
#                            'olink': 'http://',
#                            'opagelink': 'http://',
#                            'caption': 'caption'
#                            }
#            
#        path = os.path.join(os.path.dirname(__file__), 'submit.html')
#        self.response.out.write(template.render(path,template_values))
                    
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))            
        country = GetContry(self)
        if country=="cn":
            templatename="cnsubmit.html"
        else:
            templatename="submit.html"
        
        template_values = None
        host = self.request.host_url
        #file_name = ''
        error = ''
        sign_url, sign, user_name, user, user_is_admin = get_user_info()
        olink = self.request.get('olink')
        opagelink = self.request.get('opagelink')
        opagetitle = self.request.get('opagetitle')
        caption = self.request.get('caption')
        
        template_values = {
                            'user_name': user_name,
                            'user_is_admin': user_is_admin, 
                            'sign': sign,
                            'sign_url': sign_url,
                            #'img': img,
                            #'images': all,
                            'host': host,
                            'error': error,
                            'olink': olink or 'http://',
                            'opagelink': opagelink or 'http://',
                            'opagetitle': opagetitle,
                            'caption': caption or 'caption'
                            }
        path = os.path.join(os.path.dirname(__file__), templatename)
        self.response.out.write(template.render(path,template_values))
        
        
        
        
        
            
#        try:
#            result = urlfetch.fetch(url)
#            #if result.status_code == 200:
#            file_data = result.content
#            image_length = len(file_data)
#                        
            
            
            
                    
        
        
        
class Test(webapp.RequestHandler):
    def get(self,index):
        country = GetContry(self)
        if self.request.get("hl"):
            country = self.request.get("hl")
        if country=="cn":
            hl="?hl=cn"
            templatename="cnhome.html"
            version = self.request.path+"?hl=en"
            vername = "English"
        else:
            hl="?hl=en"
            templatename="home.html"
            version = self.request.path+"?hl=cn"
            vername = "中文版"
        
        
        #index = self.request.get('start')
        ImageIndex = BaseIndex.get_by_key_name("Image")
        index = int(index)
        if index<=0 or index%40!=0:
            self.redirect('/')
        realindex = ImageIndex.count-int(index)-40#*40
        if realindex < 0:
            self.redirect('/')
        else:
            indexbefore = index-40
            indexnext = index+40
            if indexbefore==0:
                indexbefore= '/'
            else:
                indexbefore= '/start/%d' % indexbefore
                indexnext = '/start/%d' % indexnext
              
            #img_paginator = paginator.Paginator(3,'index')
            #images = img_paginator.get_page(db.Query(Image).ancestor(ImageIndex),0,True)
            #self.response.out.write("OK")
            #self.response.out.write(images)
            q = Image.all().filter("index >=", realindex)
            #q.order('-date')
            
            images=q.fetch(40)
            #for img in images:
            #    self.response.out.write(img.olink+'<br/><br/>')
            template_values = None
            host = self.request.host_url 
            error = ''  
            sign_url, sign, user_name, user, user_is_admin = get_user_info()     
            # imagescoll=ImgCol(images)
            template_values = {
                        'user_name': user_name,
                        'user_is_admin': user_is_admin, 
                        'sign': sign,
                        'sign_url': sign_url,
                        'images': images,
                        'host': host,
                        'setting': True,
                        'error': error,
                        'before':str(indexbefore)+hl,
                        'next':str(indexnext)+hl,
                        'version':version,
                        'vername':vername
                        }
                                
            path = os.path.join(os.path.dirname(__file__), templatename)
            self.response.out.write(template.render(path,template_values))

class MyPicPage(webapp.RequestHandler):
    def get(self,index):
        country = GetContry(self)
        if self.request.get("hl"):
            country = self.request.get("hl")
        if country=="cn":
            hl="?hl=cn"
            templatename="cnhome.html"
            version = self.request.path+"?hl=en"
            vername = "English"
        else:
            hl="?hl=en"
            templatename="home.html"
            version = self.request.path+"?hl=cn"
            vername = "中文版"
        
        
        #index = self.request.get('start')
        sign_url, sign, user_name, user, user_is_admin = get_user_info()
        if user == None:
            self.redirect('/')
        else:            
            ImageIndex = BaseIndex.get_by_key_name(user_name)
            index = int(index)
            if index<=0 or index%40!=0:
                self.redirect('/')
            realindex = ImageIndex.count-int(index)-40#*40
            if realindex < 0:
                self.redirect('/')
            else:
                indexbefore = index-40
                indexnext = index+40
                if indexbefore==0:
                    indexbefore= '/mypic'
                else:
                    indexbefore= '/u/%d' % indexbefore
                    indexnext = '/u/%d' % indexnext
                  
                #img_paginator = paginator.Paginator(3,'index')
                #images = img_paginator.get_page(db.Query(Image).ancestor(ImageIndex),0,True)
                #self.response.out.write("OK")
                #self.response.out.write(images)
                q = Image.all()
                q.filter("owner =",user)
                q.filter("uindex >=", realindex)
                #q.order('-date')
                
                images=q.fetch(40)
                #for img in images:
                #    self.response.out.write(img.olink+'<br/><br/>')
                template_values = None
                host = self.request.host_url 
                error = ''  
                     
                # imagescoll=ImgCol(images)
                template_values = {
                            'user_name': user_name,
                            'user_is_admin': user_is_admin, 
                            'sign': sign,
                            'sign_url': sign_url,
                            'images': images,
                            'host': host,
                            'setting': True,
                            'error': error,
                            'before':str(indexbefore)+hl,
                            'next':str(indexnext)+hl,
                            'version':version,
                            'vername':vername
                            }
                                    
                path = os.path.join(os.path.dirname(__file__), templatename)
                self.response.out.write(template.render(path,template_values))

        
            
            
class Manage(webapp.RequestHandler):
    def post(self):
        
        template_values = None
        host = self.request.host_url
        file_name = ''
        error = ''
        file_content_type = ''
        ext_thumbnail = ''
        ext_original = ''
                
        sign_url, sign, user_name, user, user_is_admin = get_user_info()
        
        if self.request.get('action') == 'Del':
            keys = self.request.get('image',allow_multiple=True)
            for key in keys:
                img = get_image(key)
                if img:
                    img.delete()
        
        img = None
            
        if ('file' in self.request.POST and 
           self.request.POST.get('file', None) is not None and 
           self.request.POST.get('file', None).filename):
            
            file_data = self.request.POST.get('file').file.read()
            
            image_length = len(file_data)
            
            if image_length > config.max_size:
                error = 'File is too large'
            else:
                file_content_type = self.request.POST.get('file').type
                file_name = self.request.POST.get('file').filename
                caption = self.request.POST.get('caption')
                olink = self.request.POST.get('olink')
                opagelink = self.request.POST.get('opagelink')
                
                try:
                    ext_original, ext_thumbnail, o_encoding  = get_image_extension(file_content_type)
                    
                    img = Image()
                    img.name = file_name
                    img.original = db.Blob(file_data)
                    img.thumbnail = db.Blob(images.resize(file_data, config.thumbnail_size['width'],
                                                          config.thumbnail_size['height'],
                                                          output_encoding=o_encoding))
                    img.type = file_content_type
                    img.ext = ext_original
                    img.owner = user
                    img.caption = caption
                    img.olink = olink
                    img.opagelink = opagelink
                    img.length = image_length
                    img.ext_thumb = ext_thumbnail
                    img.put()
                    
                    img_key = str(img.key())
                    
                    memcache.set(img_key,img)
                    
                except Exception, e:
                    logging.exception(e)
                    error = 'Image error processing'

                logging.info('File name : %s' % file_name)
                logging.info('Type : %s' % file_content_type)
                logging.info('Length : %s' % image_length)
                logging.info('Owner : %s' % user)
        
        all = Image.all()
        all.order('-date')
        all = all.fetch(40)
                                
        template_values = {
                    'user_name': user_name,
                    'user_is_admin': user_is_admin, 
                    'sign': sign,
                    'sign_url': sign_url,
                    'img': img,
                    'images': all,
                    'host': host,
                    'error': error
                    }

        path = os.path.join(os.path.dirname(__file__), 'manage.html')
        self.response.out.write(template.render(path,template_values))
        
    get=post
        
class TestApp(webapp.RequestHandler):
    def get(self):
#        q = Image.all()
#        #q.order("-date")
#        q.filter("server =", "images")
#        self.response.out.write(q.count())
#        results = q.fetch(100)
#        for img in results:
#            img.server="y44y"
#            img.put()
        #img = Image.get("agR5NDR5cgwLEgVJbWFnZRjUFgw")
        #img.delete()
        self.response.out.write("good")
        #add_3p_to_server()
        #self.response.out.write("OK")
        #add_3p_to_server() 
#        url="http://imageserver1.appspot.com/submit"
#        values = urllib.urlencode({'olink' : "http://images.kangye.org/images/agR5NDR5cgwLEgVJbWFnZRjvFAw.jpg",\
#                                    'strkey' : "secondimage" })
#        result=urlfetch.fetch(url=url,payload=values,\
#                                                     method=urlfetch.POST)
#        self.response.out.write(result.content)
#        content = urlfetch.fetch("http://www.baidu.com/img/baidu_logo.gif").content
#        client = gdata.photos.service.PhotosService()
#        gdata.alt.appengine.run_on_appengine(client)
#        client.email = "areyoulookon@gmail.com"
#        client.password = "WWWg00gl3C0M"
#        client.source = 'images.kangye.org'
#        client.ProgrammaticLogin()
#        album_url = '/data/feed/api/user/%s/albumid/%s' % ("areyoulookon@gmail.com", "BgtZXI")
#        photo = client.InsertPhotoSimple('BgtZXI', 'New Photo', 
#            'Uploaded using the API',db.Blob(content),content_type='image/jpeg' )
        
        
        
        
#        url="http://bbs.sjtu.cn/bbslogin"
#        values = urllib.urlencode({'id' : "areyoulookon",'pw' : "1988315",'submit' : '' })
#        result=urlfetch.fetch(url=url,payload=values,\
#                                              method=urlfetch.POST)
#        self.response.out.write(result.content)
        
        #publishfanfou("test fanfou api")
        #self.response.out.write(self.request.remote_addr)
#        session = friendfeed.FriendFeed('lookon','dire711math')
#        entry = session.publish_link(
#                    title="Testing the FriendFeed API",
#                    link="http://images.kangye.org/",
#                    image_urls=[
#                        "http://images.kangye.org/images/agR5NDR5cgwLEgVJbWFnZRjOCww.jpg",
#                        "http://images.kangye.org/thumbs/agR5NDR5cgwLEgVJbWFnZRjMCww.jpg",
#                    ],
#                )

        
        
        
        
class Admin(webapp.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            self.redirect('/')
            return
        
        logging.info('Action : user is admin = %s', users.is_current_user_admin())
        
        action = self.request.get('action')
        
        if action == 'view':
            key = self.request.get('key')
            if key:
                pass
            else:
                for im in Image.all():
                    self.response.out.write('Image : %s | %s | %s | %s | %s<br />\n' % (im.name, im.key().name(), im.length, im.type, im.owner))
        elif action == 'delall':
            for im in Image.all():
                self.response.out.write('Image deleted : %s | %s | %s | %s | %s<br />\n' % (im.name, im.key().name(), im.length, im.type, im.owner))
                im.delete()

def get_image(key, use_memcache=False):
  
  img = memcache.get(key) if use_memcache else None
   
  if img is not None:
     logging.info('Memcache key : %s ', key)
     return img
  else:
     try:
         img = Image.get(key)
         memcache.add(key, img)
     except:
         pass
     return img

def get_random_pic(num):
    ImageIndex = BaseIndex.get_by_key_name("Image")
    count = ImageIndex.count
    random.seed()
    rannum=random.randint(1, count)
    logging.info('Random : %d' % rannum)
    if rannum+num>count:
        query = Image.all().filter("index <=", rannum)
        images = query.fetch(num)
    else:
        query = Image.all().filter("index >=", rannum)
        images = query.fetch(num)
    return images
        
def get_random_pic_by_category(category,num):
    q = Image.all()
    q = q.filter("category =", category)
    count = q.count() 
    q.order("-date")
    images = q.fetch(50)        
    if num>count:        
        logging.info("num>count")
        return get_random_pic(num)
    else:
        #q.order("date")
#        images = []
#        for i in range(2,6):
#            images.append(q[i])
        logging.info("by %s" % category)
        return random.sample(images,num)



def get_user_info():
    user = users.get_current_user()
        
    if user:
        sign_url = users.create_logout_url('/')
        sign = 'Sign out'
        user_name = users.get_current_user().email()
        is_admin = users.is_current_user_admin()
    else:
        sign_url = users.create_login_url('/')
        sign = 'Sign in'
        user_name = ''
        is_admin = False

    return sign_url, sign, user_name, user, is_admin

def get_image_extension(type):
    enc = {'image/png':['.png','.png',images.PNG],
                'image/jpeg':['.jpg','.jpg',images.JPEG],
                'image/gif':['.gif','.png',images.PNG],
                'image/bmp':['.bmp','.jpg',images.JPEG],
                'image/tiff':['.tif','.jpg',images.JPEG],
                'image/icon':['.ico','.png',images.PNG]}
    
    return enc[type][0], enc[type][1], enc[type][2]   

def get_myimage_extension(type):
    enc = {'png':['.png','.png',images.PNG],
                       'PNG':['.png','.png',images.PNG],
                       'jpg':['.jpg','.jpg',images.JPEG],
                       'JPG':['.jpg','.jpg',images.JPEG],
                       'gif':['.gif','.png',images.PNG],
                       'GIF':['.gif','.png',images.PNG],
                       'BMP':['.bmp','.jpg',images.JPEG],
                       'bmp':['.bmp','.jpg',images.JPEG],
                       'tif':['.tif','.jpg',images.JPEG],
                       'TIF':['.tif','.jpg',images.JPEG],
                       'ico':['.ico','.png',images.PNG],
                       'ICO':['.ico','.png',images.PNG]}
           
    return enc[type][0], enc[type][1], enc[type][2]  

def request_to_server(server,olink,strkey):    
    url="http://imageserver%d.appspot.com/submit" % server
    values = urllib.urlencode({'olink' : olink,\
                                'strkey' : strkey })
    result=urlfetch.fetch(url=url,payload=values,\
                                                 method=urlfetch.POST)
    return result.content

 
 
 
def add_3p_to_server():
    board = "PIC"
    url="http://bbs.sjtu.edu.cn/bbsrss?board=%s" % board
    result=urlfetch.fetch(url)
    result=result.content
    feed=feedparser.parse(result)
    entries=feed.entries
    for entry in entries:
        link = entry.link
        title = entry.title
        if title.find("Re")==-1:
            content=urlfetch.fetch(link).content                
            parser = IMGLister()
            parser.feed(content)
            parser.close()
            for url in parser.urls:
                url = "http://bbs.sjtu.edu.cn"+url
                strkey = url.replace(".","")
                strkey = strkey.replace("/","")
                rannum=random.randint(1, 4)
                request_to_server(rannum,url,strkey)
                logging.info('Add_Pic : %s %s %s' % (url,link,title))


    
    
    

def main():
    application = webapp.WSGIApplication([('/', Home),
                                          ('/admin', Admin),
                                          ('/imgdetail/(.*)',Detail),
                                          ('/(images|thumbs)/(.*)\..*',GetImage),
                                          ('/manage',Manage),
                                          ('/submit',Submit),
                                          ('/search',Search),
                                          ('/home',MainPage),
                                          ('/mypic',MyPic),
                                          ('/savecap',SaveCap),
                                          ('/test',TestApp),
                                          ('/start/(.*)',Test),
                                          ('/u/(.*)',MyPicPage),
                                          ('/sitemap.xml',Sitemap),
                                          ('/rss',RSS),
                                          ('/(.*)',Error404)],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
