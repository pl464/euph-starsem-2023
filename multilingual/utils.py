import pandas as pd
import re

# Below are the functions used to crop and tag the text.
# The main function for this is automated_crop_and_tag().

'''
helper function for get_cropped_context().

args: tokenized text, tokenized euphemism
returns: first and last position of euphemism in tokenized text
'''
def get_euph_pos(text, euph):
    # split_text = list(map(lambda x: x.lower(), split_text)) # need to ignore case for now
    # for each word in the text
    for x in range(0, len(text)-1):
        # check if the word is the first word of the euph
        if (text[x] == euph[0]):
            # if it is, need to make sure it's the whole euph (e.g., in "armed conflict", need to make sure we didn't just find "armed soldier")
            if (text[x:x+len(euph)] == euph):
                # in this case, return their position
                return x, x+(len(euph)-1)
    # otherwise, the euph wasn't found in the text (should not happen)
    return -1, -1

'''
helper function for automated_crop_and_tag().

returns cropped context given text and euphemism, and place the euphemism in <>
the idea is to obtain the position of the euphemism in the text, and look fowards/backwards
for two <s> boundaries, indicating the boundary of the preceding/following sentences

args: string containing the text, string containing the euphimism
returns: a string containing the cropped context
'''
def get_cropped_tagged_context(text, euph):
    # this is to handle euphemisms with hyphens
    if '-' in euph:
        euph = euph.replace('-', ' - ')
        
    # begin by tokenizing the text and euphemism by whitespace 
    # tokenized = text.split()
    tokenized = [*text]
    # tok_euph = euph.split()
    euph = [*euph]
    # we need the position of the euphemism so we can look backwards/forwards from it 
    pos1, pos2 = get_euph_pos(tokenized, euph)
    
    # the below ideally shouldn't happen
    # but this allows program to keep running if it does
    if (pos1 == -1 and pos2 == -1):
        return "" # we can tell this happened if there is a blank edited_text
    
    # add the tags
    tokenized[pos1] = "<" + tokenized[pos1]
    tokenized[pos2] = tokenized[pos2] + ">"

    # these variables will indicate where the cropped context begins/ends
    context_begin = 0 # assume the first word of the text
    context_end = len(tokenized)-1 # assume the last word of the text

    # find context_begin
    saw_first_sent_tag = False # have we seen one sentence tag yet?
    while (pos1 > 0):
        # print(tokenized[pos1-4:pos1-1])
        # rint(''.join(tokenized[pos1-4:pos1-1]))
        trichar_ptr = ''.join(tokenized[pos1-4:pos1-1])
        if (trichar_ptr == '<s>'):
            if (saw_first_sent_tag):
                context_begin = pos1
                break
            else:
                saw_first_sent_tag = True
        pos1 -= 1

    # find context_end
    saw_first_sent_tag = False
    while (pos2 < len(tokenized)-1):
        trichar_ptr = ''.join(tokenized[pos2+1:pos2+4])
        if (trichar_ptr == '<s>'):
            if (saw_first_sent_tag):
                context_end = pos2
                break
            else:
                saw_first_sent_tag = True
        pos2 += 1
    
    # put together the cropped text
    cropped_context = ""
    for token in tokenized[context_begin:context_end+1]:
        cropped_context += token + ''
        
    return cropped_context

'''
main wrapper function for cropping each text and attempting to clean it up a bit.
returns cropped context given text and euphemism, and place the euphemism in <>
the idea is to obtain the position of the euphemism in the text, and look fowards/backwards
for two <s> boundaries, indicating the boundary of the preceding/following sentences

args: the dataframe of texts
returns: a string containing the cropped context
'''

# Begin by copying over original text, removing HTML tags, replacing punctuation marks followed by capital letters with a
# sentence boundary "<s>" (this assumption seems to hold for almost all cases), and other preprocessing tasks:

def automated_crop_and_tag(df, text_col):
    # Remove HTML tags
    df['edited_text'] = df['orig_text'].str.replace('( <.*?>|&lt;.*?&gt;)', '')

    # Replace corpus question marks occurring between 2 lowercase letters with an apostrophe
    df['edited_text'] = df['edited_text'].str.replace('(?<=([a-z]|I)) \? (?=[a-z])', ' \'')

    # Replace isolated periods, question marks, exclamation marks and periods + quotation marks with a sentence boundary <s>
    df['edited_text'] = df['edited_text'].str.replace('。', '。 <s> ')
    df['edited_text'] = df['edited_text'].str.replace('？', '？ <s> ')
    df['edited_text'] = df['edited_text'].str.replace('！', '！ <s> ')
    df['edited_text'] = df['edited_text'].str.replace('$', ' <s> ')
    # df['edited_text'] = df['edited_text'].str.replace(' \!( |$)(?=\"?([A-Z]|$))', ' ! <s> ')

    # Treat hyphens and slashes as separate tokens (e.g. to identify "chest-thumping" or "overweight/obese")
    df['edited_text'] = df['edited_text'].str.replace('-', ' - ')
    df['edited_text'] = df['edited_text'].str.replace('/', ' / ')

    pd.set_option('display.max_colwidth', 0) # Wrap text when viewing df

    # df # shows the preprocessed / sentence-separated text

    # Here we do the actual cropping, going through each row in the df:
    for i, row in df.iterrows():
        text = df.loc[i, 'edited_text']
        keyword = df.loc[i, 'PET']
        df.loc[i, 'edited_text'] = get_cropped_tagged_context(text, keyword)

#     # df # shows the cropped and tagged text

#     # The code below removes the sentence boundary tags that were put in, undoes the preprocessing tasks, and
#     # attempts to clean up spacing (however, the spacing can remain messy in some of the cases)

    # remove <s> tags
    df['edited_text'] = df['edited_text'].str.replace(r' <s>', r'')

#     # remove opening/closing spaces between parens/quotes, and before punctuation marks
#     df['edited_text'] = df['edited_text'].str.replace(r'\( (.*?) \)', r'(\1)')
#     df['edited_text'] = df['edited_text'].str.replace(r'"\s(.*?)\s"', r'"\1"')
#     df['edited_text'] = df['edited_text'].str.replace(r'\s([.,?!:;\'])', r'\1')

#     # remove spaces before contractions
#     df['edited_text'] = df['edited_text'].str.replace(r' (?!I)([A-Za-z]\'[A-Za-z]+)', r'\1')

#     # undo spaces around hyphens and slashes
#     df['edited_text'] = df['edited_text'].str.replace(r'\s-\s', r'-')
#     df['edited_text'] = df['edited_text'].str.replace(r'\s/\s', r'/')

    # df # shows cleaned text

    return df

'''
function for adding and populating a category column into the input df, using euphsample

args: the dataframe, the CSV of euphemisms with their categories
returns: a dataframe with the additional category column
'''
def add_category_column(df, euph_list):
    euph_list['euphemism'] = euph_list['euphemism'].fillna('').apply(lambda x: x.lower()) # lowercase the euphs
    df["category"] = "" # create new column
    for i, row in df.iterrows(): # for each row in the df
        euph = df.loc[i, 'keyword'] # get the current euph
        target = euphsample.loc[euphsample['X- phemism'] == euph] # lookup the euph in euphsample
        
        if (target.empty): # if euph not found, print a message, and move onto next row
            print('{}: category not found.'.format(euph))
            continue
        
        df.loc[i, 'category'] = target.iloc[0]['category'] # get the category and place into df

    # df
    return df

'''
given an annotated dataframe, makes dataframes of counts of 0s and 1s, at the category and keyword level.
this function also displays them. this is intended to help decide how to balance the euph counts.

args: the annotated dataframe
returns: a dataframe with counts for categories, and a dataframe with counts for keywords
'''
def get_counts(df):
    categories = { # category: [0s, 1s, total]
                'bodily functions': [0, 0, 0],
                'death': [0, 0, 0],
                'employment': [0, 0, 0], 
                'physical/mental attributes': [0, 0, 0],
                'politics': [0, 0, 0],
                'sexual activity': [0, 0, 0],
                'substances': [0, 0, 0]
               }

    for i, row in df.iterrows():
        category = df.loc[i, 'category']
        is_euph = int(df.loc[i, 'is_euph'])
        category = category.strip()
        categories[category][is_euph] += 1
        categories[category][2] += 1
            
    categories_list = []
    zeros = []
    ones = []
    totals = []

    for key, value in categories.items():
        categories_list.append(key)
        zeros.append(value[0])
        ones.append(value[1])
        totals.append(value[2])

    categories_dict = {
         'categories': categories_list, 
         '0s': zeros,
         '1s': ones,
         'total': totals
        }
    category_counts = pd.DataFrame(data=categories_dict)
    display(category_counts)

    # now, we do the same, but for the keywords

    keywords = {}

    for i, row in df.iterrows(): 
        keyword = df.loc[i, 'keyword'] 
        is_euph = int(df.loc[i, 'is_euph'])
        if (keyword not in keywords):
            keywords[keyword] = [0, 0, 1]
        else:
            keywords[keyword][2] += 1
        keywords[keyword][is_euph] += 1
            
    euph_list = []
    zeros = []
    ones = []
    totals = []

    for key, value in keywords.items():
        euph_list.append(key)
        zeros.append(value[0])
        ones.append(value[1])
        totals.append(value[2])

    euphs_dict = {
     'euph': euph_list, 
     '0': zeros,
     '1': ones,
     'total': totals
    }
    euph_counts = pd.DataFrame(data=euphs_dict)
    pd.set_option('display.max_rows', 1000) # or 1000.
    display(euph_counts)

    return category_counts, euph_counts

'''
modified version of get_cropped_tagged_context(); crops everything but sentence containing the euphemism

returns the sentence that the target phrase is in.
the idea is to obtain the position of the euphemism in the text, and look fowards/backwards
for <s> boundaries, indicating the boundary of the sentence

args: string containing the text, string containing the euphimism
returns: a string containing the cropped context
'''
def get_single_sentence_context(text, euph):
    # this is to handle euphemisms with hyphens
    if '-' in euph:
        euph = euph.replace('-', ' - ')
        
    # begin by tokenizing the text and euphemism by whitespace 
    tokenized = text.split()
    tok_euph = euph.split()
    
    # we need the position of the euphemism so we can look backwards/forwards from it 
    pos1, pos2 = get_euph_pos(tokenized, tok_euph)
    
    # the below ideally shouldn't happen
    # but this allows program to keep running if it does
    if (pos1 == -1 and pos2 == -1):
        return "" # we can tell this happened if there is a blank edited_text

    # these variables will indicate where the cropped context begins/ends
    context_begin = 0 # assume the first word of the text
    context_end = len(tokenized)-1 # assume the last word of the text

    # find context_begin
    saw_first_sent_tag = False # have we seen one sentence tag yet?
    while (pos1 > 0):
        if (tokenized[pos1-1] == '<s>'):
            #if (saw_first_sent_tag):
            context_begin = pos1
            break
        pos1 -= 1

    # find context_end
    saw_first_sent_tag = False
    while (pos2 < len(tokenized)-1):
        if (tokenized[pos2+1] == '<s>'):
            context_end = pos2
            break
        pos2 += 1
    
    # put together the cropped text
    cropped_context = ""
    for token in tokenized[context_begin:context_end+1]:
        cropped_context += token + ' '
        
    return cropped_context
