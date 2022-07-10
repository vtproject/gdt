def main(source_url, link):

    print(source_url)
    print(link)
    
    source_path_list = source_url.split("/") #rozdělení úrovní cesty zdrojové url do seznamu
    
    link = link.split("#")[0] #odstranění odkazu na heading
    
    if ".." in link:
        link = link.split("../")[-1] #odstranění ../ na začátku odkazu
        source_path_list[-2] = link #posun v cestě o jednu úroveň výše
        del source_path_list[-1] #odstranění poslední části cesty
    else:
        source_path_list[-1] = link #nahrazení poslední části cesty
    
    full_url = "/".join(source_path_list) #sloučení částí cesty zpět do url
    
    print(full_url, "\n")
    
    return(full_url) #vrací novou kompletní url