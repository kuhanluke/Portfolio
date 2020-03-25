import pandas as pd

class recommendation():
    def __init__(self, movies, cosine_sim):
        # cosine_sim query
#         query = '''
#         select *
#         from cosine_sim
#         '''
         # pull from sql and convert columns
#         self.cosine_sim = pd_sql.read_sql(query, sql_conn)
#         self.cosine_sim.columns = self.cosine_sim.columns.astype(int)
        self.movies = movies
        self.cosine_sim = cosine_sim
        self.fullindices = movies.title + ' (' + movies.year.astype(str) + ')'

    def indices(self):
        return self.fullindices

    def recommend(self, title, year):
        movies = self.movies
        fullindices = self.fullindices
        recommended_movies = []
    #     title = title.lower()
        print(title)
        gen1 = list(movies[(movies.title == title) & (movies.year == year)].genres)[0]
        col1 = list(movies[(movies.title == title) & (movies.year == year)].belongs_to_collection)[0]
        title = title + ' (' + str(year) + ')'
        idx = fullindices[fullindices == title].index[0]
        score_series = pd.Series(self.cosine_sim[idx]).sort_values(ascending = False)
    #     print(score_series[:10])
        top_10_indices = list(score_series.iloc[1:51].index)
    #     print(top_10_indices)
    #     print(gen1)
        if col1 == None:
            col1 = 'xoxogossipgirl'

        for i in top_10_indices:
            recommended_movies.append(list(fullindices)[i])

        rec_movies = []
        for i in recommended_movies:
            title2 = i[:-7]
            year2 = int(i[-5:-1])
            rating = list(movies[(movies.title == title2) & (movies.year == year2)].vote_average)[0]
            gen2 = list(movies[(movies.title == title2) & (movies.year == year2)].genres)[0]
            col2 = list(movies[(movies.title == title2) & (movies.year == year2)].belongs_to_collection)[0]
            if (rating > 6) & (len(gen1+gen2) > len(set(gen1+gen2))) & (col1 != col2):
                rec_movies.append(i)

        return rec_movies[:6]
    
    def posters(self, title, year):
        movies = self.movies
        rec_movies = self.recommend(title, year)
        posterlist = []
        for i in rec_movies:
            title = i[:-7]
            year = int(i[-5:-1])
            poster = list(movies[(movies.title == title) & (movies.year == year)].poster)[0]
            poster = 'https://image.tmdb.org/t/p/w1280' + poster[31:]
            posterlist.append(poster)
        return posterlist
    
    def links(self, title, year):
        movies = self.movies
        rec_movies = self.recommend(title, year)
        linklist = []
        for i in rec_movies:
            title = i[:-7]
            year = int(i[-5:-1])
            imdbid = list(movies[(movies.title == title) & (movies.year == year)].imdb_id)[0]
            link = 'https://www.imdb.com/title/' + imdbid
            linklist.append(link)
        return linklist