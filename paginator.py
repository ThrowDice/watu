#Copyright 2008 Adam A. Crossland
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

from google.appengine.ext import db
import copy

class PaginatedList(list):
    """An extended normal Python list with three additional properties used for
    pagination purposes:
    prev_index - the starting index of the previous page of entities;
    next_index - the starting index of the next page of entities;
    curr_index - the starting index of the current page of entities
    """
    def __init__(self, *args, **kw):
        list.__init__(self, *args, **kw)
        self.prev_index = None
        "The starting index of the previous page of entities"
        self.next_index = None
        "The starting index of the next page of entities"
        self.curr_index = None
        "The starting index of the current page of entities"
   
class Paginator:
    "A class that supports pagination of AppEngine Datastore entities."
    def __init__(self, page_size, index_field):
        self.page_size = page_size
        "The number of entities that constitute a 'page'"
        self.index_field = index_field
        "The name of the field in the Model that is a orderable index"

    def get_page(self, query=None, start_index=None, ascending=True):
        """Takes a normal AppEngine Query and returns paginated results.
        query - a Datastore Query object.  It must not have an order clause.
        start_index - the index of the first record in the desired page.  If the
            index is not known, or the first page is needed, None should be
            passed.
        ascending - True if the index column is to be ordered ascending; False
            should be passed for descending ordering.
        """
       
        fetched = None
       
        # I need to make a copy of the query, as once I use it to get the main
        # collection of desired records, I will not be able to re-use it to get
        # the next or prev collection.
        query_copy = copy.deepcopy(query)
       
        if ascending:
            # First, I will grab the requested page of entities and determine
            # the index for the next page
            filter_on = self.index_field + " >="
            fetched = PaginatedList(query.filter(filter_on, start_index).order(self.index_field).fetch(self.page_size + 1))
            if len(fetched) > 0:
                # The first row that we get back is the real index.
                fetched.curr_index = fetched[0].index
            if len(fetched) > self.page_size:
                # We fetched one more record than we actually need.  That is the
                # index of the first record of the next page.  Record it, and
                # delete the extra record from our collection.
                fetched.next_index = fetched[-1].index
                del(fetched[-1])
            # Now, I will try to determine the index of the previous page
            filter_on = self.index_field + " <"
            previous_page = query_copy.filter(filter_on, start_index).order("-" + self.index_field).fetch(self.page_size)
            if len(previous_page) > 0:
                # The last record is the first record in the previous page.
                # Record it.
                fetched.prev_index = previous_page[-1].index
        else:
            # Follow the same logical pattern as for ascending, but reverse
            # the polarity of the neutron flow
            filter_on = self.index_field + " <="
            fetched = PaginatedList(query.filter(filter_on, start_index).order("-" + self.index_field).fetch(self.page_size + 1))
            if len(fetched) > 0:
                # The first row that we get back is the real index.
                fetched.curr_index = fetched[0].index           
            if len(fetched) > self.page_size:
                # We fetched one more record than we actually need.  That is the
                # index of the first record of the next page.  Record it, and
                # delete the extra record from our collection.
                fetched.next_index = fetched[-1].index
                del(fetched[-1])
            # Determine index of previous page
            filter_on = self.index_field + " >"
            previous_page = query_copy.filter(filter_on, start_index).order(self.index_field).fetch(self.page_size)
            if len(previous_page) > 0:
                # The last record is the first record in the previous page.
                # Record it.
                fetched.prev_index = previous_page[-1].index
               
        return fetched
