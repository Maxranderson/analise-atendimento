
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard Clínica")

st.title("Dashboard Clínica")
f=st.file_uploader("Arquivo XLSX",type="xlsx")
if not f: st.stop()
df=pd.read_excel(f)
cols=df.columns.tolist()
df.columns=["Data","Paciente","Contato","Horario","Agendado por","Status","Categoria","Plano","Clinica","Profissional","Cadeira"][:len(df.columns)]
for c,v in [("Status","Sem Status"),("Categoria","Sem Categoria"),("Profissional","Desconhecido")]:
    df[c]=df[c].fillna(v).replace("",v)
def dur(h):
    try:
        a,b=[x.strip() for x in h.split("às")]
        t1=pd.to_datetime(a,format="%H:%M");t2=pd.to_datetime(b,format="%H:%M")
        return (t2-t1).seconds/60
    except: return None
df["Duracao"]=df["Horario"].astype(str).apply(dur)
no_show=(df["Status"].astype(str).str.contains("6-Faltou",case=False)).mean()*100
c1,c2=st.columns(2)
c1.metric("Taxa No-Show",f"{no_show:.1f}%")
c2.metric("Agendamentos",len(df))

interno=df["Paciente"].astype(str).str.contains(r"\(.*compromisso.*\)",case=False,regex=True)

hrs=[]
for h in df["Horario"].astype(str):
    try: hrs.append(h.split("às")[0].strip()[:2]+":00")
    except: pass

col1, col2 = st.columns(2)
with col1:
    st.subheader("Atendimentos por profissional")
    profissionais = (
        df["Profissional"]
        .value_counts()
        .reset_index()
    )

    profissionais.columns = ["Profissional", "Quantidade"]

    fig = px.pie(
        profissionais,
        names="Profissional",
        values="Quantidade",
        hole=0.45,  # deixa no estilo donut; use 0 para pizza tradicional
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        legend_title="Profissional",
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)
    
with col2:
    st.subheader("Compromissos internos vs atendimentos")
    st.write(pd.DataFrame({"Tipo":["Internos","Atendimentos"],"Qtd":[interno.sum(),(~interno).sum()]}).set_index("Tipo"))

    

col3, col4 = st.columns(2)
with col3:
    st.subheader("Categorias")
    st.bar_chart(df["Categoria"].value_counts())
    
    tmp=df.dropna(subset=["Duracao"])
    opt=st.selectbox("Tempo médio em minutos por",["Categoria","Profissional"])
    st.bar_chart(tmp.groupby(opt)["Duracao"].mean())
with col4:
    st.subheader("Ocupação por hora")
    st.bar_chart(pd.Series(hrs).value_counts().sort_index())

    
    
    

