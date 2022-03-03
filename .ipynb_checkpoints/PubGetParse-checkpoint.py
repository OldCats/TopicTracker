import urllib3
http = urllib3.PoolManager()
import re
import xml.etree.ElementTree as ET
from time import strptime
import html

# Function to get PubMed IDs from the query
def get_p_ids(query):
    url_getp_ids = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=100000&term=replacethis"
    url_getp_ids = url_getp_ids.replace("replacethis", query)
    content = http.request("GET", url_getp_ids)
    content = content.data.decode("utf-8")
    root = ET.fromstring(content)
    # get IDs
    idlist = []
    for x in root.findall('IdList/Id'):
        value = x.text
        idlist.append(value)
    return(idlist)

# Function to download and parse the article to a single line (I don't really like it, I keep it here just for documentation purposes)
'''def get_parse_article(p_id):
    line = []
    url_getcontent = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=replacethis"
    url_getcontent = url_getcontent.replace("replacethis", p_id)
    content = http.request("GET", url_getcontent)
    article = content.data.decode("utf-8")
    root = ET.fromstring(article)
    pmid = str(p_id)
    #Case: is book
    checkbook = root.find("PubmedBookArticle")
    if checkbook is not None:
        pid_type = "Book"
        year = root.find("PubmedBookArticle/BookDocument/Book/PubDate/Year")
        if year is None:
            year = ""
        else:
            year = year.text
        journal = "NA"
        publisher = root.find("PubmedBookArticle/BookDocument/Book/Publisher/PublisherName")
        if publisher is None:
            publisher = ""
        else:
            publisher = publisher.text
        title = root.find("PubmedBookArticle/BookDocument/Book/BookTitle")
        if title is None:
            title = ""
        else:
            title = title.text
        abstract = root.find("PubmedBookArticle/BookDocument/Abstract/AbstractText")
        if abstract is None:
            abstract = ""
        else:
            abstract = abstract.text
        lastnamelist = []
        for x in root.findall("PubmedBookArticle/BookDocument/Book/AuthorList/Author/LastName"):
            lastname = x.text
            lastnamelist.append(lastname)
        lastnamelist = ", ".join(item for item in lastnamelist if item)
        language = root.find("PubmedBookArticle/BookDocument/Book/Language")
        if language is None:
            language = ""
        else:
            language = language.text
        meshtermlist = "NA"
        keywordlist = "NA"
        line.extend((pmid, pid_type, year, journal, publisher, title, abstract, lastnamelist, language, meshtermlist, keywordlist))
        # Case: is article
    checkarticle = root.find("PubmedArticle")
    if checkarticle is not None:
        pid_type = "Article"
        year = root.find("PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
        if year is None:
            year = root.find("PubmedArticle/MedlineCitation/Article/ArticleDate/Year")
            if year is None:
                year = root.find("PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate")
                if year is None:
                    year = ""
                else:
                    year = year.text
                    match = re.match(r'.*([1-3][0-9]{3})', year)
                    if match is not None:
                        year = match.group(1)
                    else:
                        year = ""
            else:
                year = year.text 
        else:
            year = year.text
        publisher = "NA"
        journal = root.find("PubmedArticle/MedlineCitation/Article/Journal/Title")
        if journal is None:
            journal = ""
        else:
            journal = journal.text
        title = root.find("PubmedArticle/MedlineCitation/Article/ArticleTitle")
        if title is None:
            title = ""
        else:
            title = title.text
        abstract = root.find("PubmedArticle/MedlineCitation/Article/Abstract/AbstractText")
        if abstract is None:
            abstract = ""
        else:
            abstract = abstract.text
        lastnamelist = []
        for x in root.findall("PubmedArticle/MedlineCitation/Article/AuthorList/Author/LastName"):
            lastname = x.text
            lastnamelist.append(lastname)
        lastnamelist = ", ".join(item for item in lastnamelist if item)
        language = root.find("PubmedArticle/MedlineCitation/Article/Language")
        if language is None:
            language = ""
        else:
            language = language.text
        meshtermlist = []
        for x in root.findall("PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName"):
            meshterm = x.text
            meshtermlist.append(meshterm)
        meshtermlist = ", ".join(item for item in meshtermlist if item)
        keywordlist = []
        for x in root.findall("PubmedArticle/MedlineCitation/KeywordList/Keyword"):
            keyword = x.text
            keywordlist.append(keyword)
        keywordlist = ", ".join(item for item in keywordlist if item)
        line.extend((pmid, pid_type, year, journal, publisher, title, abstract, lastnamelist, language, meshtermlist, keywordlist))
    return(line)'''

# Function to download and parse the article to a single line (with regex)
def get_parse_article_re(p_id):
    line = []
    #url_getcontent = "https://pubmed.ncbi.nlm.nih.gov/replacethis/?format=pubmed" This does not allow multiple requests, but it provides every COI statement. The following address allows multiple requests, but does not provide every COI statement. Big Bummer.
    url_getcontent = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=medline&id=replacethis"
    url_getcontent = url_getcontent.replace("replacethis", p_id)
    content = http.request("GET", url_getcontent)
    article = content.data.decode("utf-8")
    #article = re.search(r"PMID-\s[\s\S]*(?=<\/pre)", article) <- had to comment these two out due to the url_getcontent address change
    #article = article.group(0)
    newlinesmatch = re.compile(r"\n\s{2,}", re.MULTILINE)
    article = re.sub(newlinesmatch, " ", article)
    #article = html.unescape(article) <- had to comment this out due to the url_getcontent address change

    ## Pubmed id
    pmid = p_id

    ## Publication type
    typematch = re.compile(r"(?<=PT\s\s-\s).*")
    pid_type = re.findall(typematch, article)
    if pid_type is not None:
        pid_type = [i.strip() for i in pid_type]
        if ("Book Chapter" in pid_type or "book chapter" in pid_type):
            pid_type = "Book chapter"
        elif ("Book" in pid_type or "book" in pid_type):
            pid_type = "Book"
        else:
            pid_type = "Article"
    else:
        pid_type = ""

    ## Year
    year = re.search(r"(?<=DP\s\s-\s)\d*", article)
    if year is not None:
        year = (year.group(0)).strip()
    else:
        year = ""

    ## Journal
    journal = re.search(r"(?<=JT\s\s-\s).*", article)
    if journal is not None:
        journal = (journal.group(0)).strip()
    else:
        journal = ""

    ## Publisher
    publisher = re.search(r"(?<=PB\s\s-\s).*", article)
    if publisher is not None:
        publisher = (publisher.group(0)).strip()
    else:
        publisher = ""

    ## Title
    title = re.search(r"(?<=TI\s\s-\s).*", article)
    if title is not None:
        title = (title.group(0)).strip()
    else:
        title = ""

    ## Book title
    book_title = re.search(r"(?<=BTI\s-\s).*", article)
    if book_title is not None:
        book_title = (book_title.group(0)).strip()
    else:
        book_title = re.search(r"(?<=BTI\s-\s).*", article)
        if book_title is not None:
            book_title = (book_title.group(0)).strip()
        else:
            book_title = ""

    ## Abstract
    abstract = re.search(r"(?<=AB\s\s-\s).*", article)
    if abstract is not None:
        abstract = (abstract.group(0)).strip()
    else:
        abstract = ""

    ## Other abstract
    oabstract = re.search(r"(?<=OAB\s-\s).*", article)
    if oabstract is not None:
        oabstract = (oabstract.group(0)).strip()
    else:
        oabstract = ""

    ## Authors
    typematch = re.compile(r"(?<=AU\s\s-\s).*")
    authorlist = re.findall(typematch, article)
    authorlist1 = []
    if not authorlist:
        authors = ""
    else:
        for x in authorlist:
            authorlist1.append(x.strip())
        authors = ", ".join(authorlist1)

    ## Editors
    typematch = re.compile(r"(?<=ED\s\s-\s).*")
    editorlist = re.findall(typematch, article)
    editorlist1 = []
    if not editorlist:
        editors = ""
    else:
        for x in editorlist:
            editorlist1.append(x.strip())
        editors = ", ".join(editorlist1)

    ## Language
    language = re.search(r"(?<=LA\s\s-\s).*", article)
    if language is not None:
        language = (language.group(0)).strip()
    else:
        language = ""

    ## MeSH terms
    typematch = re.compile(r"(?<=MH\s\s-\s).*")
    meshlist = re.findall(typematch, article)
    meshlist1 = []
    if not meshlist:
        meshterms = ""
    else:
        for x in meshlist:
            meshlist1.append(x.strip())
        #meshterms = ", ".join(meshlist1)
        meshterms = meshlist1

    ## Keywords
    typematch = re.compile(r"(?<=OT\s\s-\s).*")
    keywordlist = re.findall(typematch, article)
    keywordlist1 = []
    if not keywordlist:
        keywords = ""
    else:
        for x in keywordlist:
            keywordlist1.append(x.strip())
        #keywords = ", ".join(keywordlist1)
        keywords = keywordlist1

    ## COI
    coi = re.search(r"(?<=COIS-\s).*", article)
    if coi is not None:
        coi = (coi.group(0)).strip()
    else:
        coi = ""

    ## DOI
    doi = re.search(r"(?<=AID\s-\s).*(?=\s\[doi)", article)
    if doi is not None:
        doi = (doi.group(0)).strip()
    else:
        doi = ""

    ## Grant
    grant = re.search(r"(?<=GR\s\s-\s).*", article)
    if grant is not None:
        grant = (grant.group(0)).strip()
    else:
        grant = ""
    
    line.extend((p_id, pid_type, year, journal, publisher, title, book_title, abstract, oabstract, authors, editors, language, meshterms, keywords, coi, grant, doi))
    return(line)

# Create a medline file (for import in reference managers) from PIDs  - after cleaning the dataframe
#url_getcontent = "https://pubmed.ncbi.nlm.nih.gov/replacethis/?format=pubmed" This does not allow multiple requests, but it provides every COI statement. The one in use (entrez) allows multiple requests, but does not provide every COI statement. Big Bummer.
def art_to_medline(p_id, filepath_medline):
    line = []
    url_getcontent = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=medline&id=replacethis"
    url_getcontent = url_getcontent.replace("replacethis", p_id)
    content = http.request("GET", url_getcontent)
    article = content.data.decode("utf-8")
    with open(filepath_medline, "a") as f:
        f.write(article + "\n")