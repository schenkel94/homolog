ALLOWED = [

"data analyst",
"analytics",
"business analyst",
"bi analyst",
"analista de dados",
"analista de negócios"

]

BLOCKED = [

"engineer",
"scientist",
"machine learning",
"ml",
"platform"

]

BRAZIL = [

"brazil",
"brasil",
"são paulo",
"sao paulo",
"rio de janeiro",
"porto alegre",
"curitiba",
"florianopolis",
"belo horizonte",
"recife"

]


def filter_jobs(df):

    if df.empty:
        return df

    df["title"] = df["title"].astype(str).str.lower()
    df["location"] = df["location"].astype(str).str.lower()

    allowed = df["title"].str.contains("|".join(ALLOWED))
    blocked = df["title"].str.contains("|".join(BLOCKED))
    brazil = df["location"].str.contains("|".join(BRAZIL))

    df = df[allowed & ~blocked & brazil]

    return df