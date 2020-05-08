from __future__ import division
import pandas as pd

from sklearn.cluster import KMeans

import plotly.plotly as py
import plotly.offline as pyoff
import plotly.graph_objs as go

from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter.filedialog import askopenfilename
import shutil

LARGE_FONT=("Verdana",12)

class Customer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.title(self,"Customer Segmentation")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0,weight = 1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
         
        for F in (StartPage, PageOne, PageTwo, Revenue, MGR, MAC,MOC, ARPO, NCR, Recency, Frequency, Monetary, RevFreSegments, RevRecSegments, FreRecSegments):
             frame = F(container, self)
             self.frames[F]= frame
             frame.grid(row=0, column=1, sticky="nsew")
        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def import_csv_data(self,controller):
        csv_file_path = askopenfilename()
        print(csv_file_path)
        v.set(csv_file_path)
        shutil.copy(csv_file_path, '../Customer/data.csv')
        
        '''
                Jupyter
                Notebook
                '''
        
        tx_data = pd.read_csv('data.csv', engine='python')

        tx_data.head(10)
        
        #converting the type of Invoice Date Field from string to datetime.
        tx_data['InvoiceDate'] = pd.to_datetime(tx_data['InvoiceDate'])
        
        #creating YearMonth field for the ease of reporting and visualization
        tx_data['InvoiceYearMonth'] = tx_data['InvoiceDate'].map(lambda date: 100*date.year + date.month)
        
        #calculate Revenue for each row and create a new dataframe with YearMonth - Revenue columns
        tx_data['Revenue'] = tx_data['UnitPrice'] * tx_data['Quantity']
        tx_revenue = tx_data.groupby(['InvoiceYearMonth'])['Revenue'].sum().reset_index()
        '''
        #Vizualize revenue
        '''
        #X and Y axis inputs for Plotly graph. We use Scatter for line graphs
        plot_data = [
                go.Scatter(
                        x=tx_revenue['InvoiceYearMonth'],
                        y=tx_revenue['Revenue'],
                        )
                ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='Montly Revenue'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./stats/revenue.png')
        
        '''
        #Monthly Revenue Growth Rate:


        '''
        #using pct_change() function to see monthly percentage change
        tx_revenue['MonthlyGrowth'] = tx_revenue['Revenue'].pct_change()
        
        #showing first 5 rows
        tx_revenue.head()
        
        #visualization - line graph
        plot_data = [
                go.Scatter(
                        x=tx_revenue.query("InvoiceYearMonth < 201112")['InvoiceYearMonth'],
                        y=tx_revenue.query("InvoiceYearMonth < 201112")['MonthlyGrowth'],
                        )
                ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='Montly Growth Rate'
                )
        
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./stats/mgr.png')
        
        '''
            # MOnthly Active Customer
        '''
        #creating a new dataframe with UK customers only
        tx_uk = tx_data.query("Country=='United Kingdom'").reset_index(drop=True)
        
        #creating monthly active customers dataframe by counting unique Customer IDs
        tx_monthly_active = tx_uk.groupby('InvoiceYearMonth')['CustomerID'].nunique().reset_index()
        
        #print the dataframe
        tx_monthly_active
        
        #plotting the output
        plot_data = [
                go.Bar(
                        x=tx_monthly_active['InvoiceYearMonth'],
                        y=tx_monthly_active['CustomerID'],
                        )
                ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='Monthly Active Customers'
                )
        
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./stats/mac.png')
        '''
       # Monthly Order Count
        '''
        #create a new dataframe for no. of order by using quantity field
        tx_monthly_sales = tx_uk.groupby('InvoiceYearMonth')['Quantity'].sum().reset_index()
        
        #print the dataframe
        tx_monthly_sales
        
        #plot
        plot_data = [
                go.Bar(
                        x=tx_monthly_sales['InvoiceYearMonth'],
                        y=tx_monthly_sales['Quantity'],
                        )
                ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='Monthly Total no. of Order'
                )
        
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./stats/moc.png')
        '''
      #  Average Revenue per Order
        '''
        # create a new dataframe for average revenue by taking the mean of it
        tx_monthly_order_avg = tx_uk.groupby('InvoiceYearMonth')['Revenue'].mean().reset_index()
        
        #print the dataframe
        tx_monthly_order_avg
        
        #plot the bar chart
        plot_data = [
                go.Bar(
                        x=tx_monthly_order_avg['InvoiceYearMonth'],
                        y=tx_monthly_order_avg['Revenue'],
                        )
                ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='Monthly Order Average'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./stats/arpo.png')
        '''
       # New Customer Ratio
        '''
        #create a dataframe contaning CustomerID and first purchase date
        tx_min_purchase = tx_uk.groupby('CustomerID').InvoiceDate.min().reset_index()
        tx_min_purchase.columns = ['CustomerID','MinPurchaseDate']
        tx_min_purchase['MinPurchaseYearMonth'] = tx_min_purchase['MinPurchaseDate'].map(lambda date: 100*date.year + date.month)
        
        #merge first purchase date column to our main dataframe (tx_uk)
        tx_uk = pd.merge(tx_uk, tx_min_purchase, on='CustomerID')
        
        tx_uk.head()
        
        #create a column called User Type and assign Existing 
        #if User's First Purchase Year Month before the selected Invoice Year Month
        tx_uk['UserType'] = 'New'
        tx_uk.loc[tx_uk['InvoiceYearMonth']>tx_uk['MinPurchaseYearMonth'],'UserType'] = 'Existing'
        
        #calculate the Revenue per month for each user type
        tx_user_type_revenue = tx_uk.groupby(['InvoiceYearMonth','UserType'])['Revenue'].sum().reset_index()
        
        #filtering the dates and plot the result
        tx_user_type_revenue = tx_user_type_revenue.query("InvoiceYearMonth != 201012 and InvoiceYearMonth != 201112")
        plot_data = [
                go.Scatter(
                        x=tx_user_type_revenue.query("UserType == 'Existing'")['InvoiceYearMonth'],
                        y=tx_user_type_revenue.query("UserType == 'Existing'")['Revenue'],
                        name = 'Existing'
                        ),
                        go.Scatter(
                                x=tx_user_type_revenue.query("UserType == 'New'")['InvoiceYearMonth'],
                                y=tx_user_type_revenue.query("UserType == 'New'")['Revenue'],
                                name = 'New'
                                )
                        ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='New vs Existing'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        #create a dataframe that shows new user ratio - we also need to drop NA values (first month new user ratio is 0)
        tx_user_ratio = tx_uk.query("UserType == 'New'").groupby(['InvoiceYearMonth'])['CustomerID'].nunique()/tx_uk.query("UserType == 'Existing'").groupby(['InvoiceYearMonth'])['CustomerID'].nunique() 
        tx_user_ratio = tx_user_ratio.reset_index()
        tx_user_ratio = tx_user_ratio.dropna()
        
        #print the dafaframe
        tx_user_ratio
        
        #plot the result
        
        plot_data = [
                go.Bar(
                        x=tx_user_ratio.query("InvoiceYearMonth>201101 and InvoiceYearMonth<201112")['InvoiceYearMonth'],
                        y=tx_user_ratio.query("InvoiceYearMonth>201101 and InvoiceYearMonth<201112")['CustomerID'],
                        )
                ]
        
        plot_layout = go.Layout(
                xaxis={"type": "category"},
                title='New Customer Ratio'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
                
        fig.write_image('./stats/ncr.png')
        
                      
        
        
        
                
        
        '''
        #end
        #of 
        #jupyter
        '''    
        
        '''
        #Customer segmentation
        '''
        #tx_data = pd.read_csv('data.csv', engine='python')
        
        #tx_data.head(10)
        
        tx_data['InvoiceDate'] = pd.to_datetime(tx_data['InvoiceDate'])
        
        #tx_data['InvoiceDate'].describe()
        
        tx_uk = tx_data.query("Country=='United Kingdom'").reset_index(drop=True)
        
        tx_user = pd.DataFrame(tx_data['CustomerID'].unique())
        tx_user.columns = ['CustomerID']
        
        tx_max_purchase = tx_uk.groupby('CustomerID').InvoiceDate.max().reset_index()
        
        tx_max_purchase.columns = ['CustomerID','MaxPurchaseDate']
        
        tx_max_purchase['Recency'] = (tx_max_purchase['MaxPurchaseDate'].max() - tx_max_purchase['MaxPurchaseDate']).dt.days
        
        tx_user = pd.merge(tx_user, tx_max_purchase[['CustomerID','Recency']], on='CustomerID')
        
        tx_user.head()
        
        tx_user.Recency.describe()
        
        plot_data = [
                go.Histogram(
                        x=tx_user['Recency']
                        )
                ]
        
        plot_layout = go.Layout(
                title='Recency'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./segment/recency.png')
        
        
        kmeans = KMeans(n_clusters=4)
        kmeans.fit(tx_user[['Recency']])
        tx_user['RecencyCluster'] = kmeans.predict(tx_user[['Recency']])
        
        tx_user.groupby('RecencyCluster')['Recency'].describe()
        
        def order_cluster(cluster_field_name, target_field_name,df,ascending):
            new_cluster_field_name = 'new_' + cluster_field_name
            df_new = df.groupby(cluster_field_name)[target_field_name].mean().reset_index()
            df_new = df_new.sort_values(by=target_field_name,ascending=ascending).reset_index(drop=True)
            df_new['index'] = df_new.index
            df_final = pd.merge(df,df_new[[cluster_field_name,'index']], on=cluster_field_name)
            df_final = df_final.drop([cluster_field_name],axis=1)
            df_final = df_final.rename(columns={"index":cluster_field_name})
            return df_final
        
        tx_user = order_cluster('RecencyCluster', 'Recency',tx_user,False)
        
        tx_frequency = tx_uk.groupby('CustomerID').InvoiceDate.count().reset_index()
        
        tx_frequency.columns = ['CustomerID','Frequency']
        
        tx_frequency.head()
        
        tx_user = pd.merge(tx_user, tx_frequency, on='CustomerID')
        
        tx_user.head()
        
        tx_user.Frequency.describe()
        
        plot_data = [
                go.Histogram(
                        x=tx_user.query('Frequency < 1000')['Frequency']
                        )
                ]
        
        plot_layout = go.Layout(
                title='Frequency'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./segment/frequency.png')
        
        kmeans = KMeans(n_clusters=4)
        kmeans.fit(tx_user[['Frequency']])
        tx_user['FrequencyCluster'] = kmeans.predict(tx_user[['Frequency']])
        
        tx_user.groupby('FrequencyCluster')['Frequency'].describe()
        
        tx_user = order_cluster('FrequencyCluster', 'Frequency',tx_user,True)
        
        # # Monetary Value
        
        tx_uk['Revenue'] = tx_uk['UnitPrice'] * tx_uk['Quantity']
        
        tx_revenue = tx_uk.groupby('CustomerID').Revenue.sum().reset_index()
        
        tx_revenue.head()
        
        tx_user = pd.merge(tx_user, tx_revenue, on='CustomerID')
        
        tx_user.Revenue.describe()
        
        plot_data = [
                go.Histogram(
                        x=tx_user.query('Revenue < 10000')['Revenue']
                        )
                ]
        
        plot_layout = go.Layout(
                title='Monetary Value'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./segment/monetary.png')
        
        import warnings
        warnings.filterwarnings("ignore")
        
        kmeans = KMeans(n_clusters=4)
        kmeans.fit(tx_user[['Revenue']])
        tx_user['RevenueCluster'] = kmeans.predict(tx_user[['Revenue']])
        
        tx_user = order_cluster('RevenueCluster', 'Revenue',tx_user,True)
        
        tx_user.groupby('RevenueCluster')['Revenue'].describe()
        
        tx_user.head()
        
        tx_user['OverallScore'] = tx_user['RecencyCluster'] + tx_user['FrequencyCluster'] + tx_user['RevenueCluster']
        
        tx_user.groupby('OverallScore')['Recency','Frequency','Revenue'].mean()
        
        tx_user.groupby('OverallScore')['Recency'].count()
        
        tx_user['Segment'] = 'Low-Value'
        tx_user.loc[tx_user['OverallScore']>2,'Segment'] = 'Mid-Value' 
        tx_user.loc[tx_user['OverallScore']>4,'Segment'] = 'High-Value' 
        
        tx_graph = tx_user.query("Revenue < 50000 and Frequency < 2000")
        
        plot_data = [
                go.Scatter(
                        x=tx_graph.query("Segment == 'Low-Value'")['Frequency'],
                        y=tx_graph.query("Segment == 'Low-Value'")['Revenue'],
                        mode='markers',
                        name='Low',
                        marker= dict(size= 7,
                                     line= dict(width=1),
                                     color= 'blue',
                                     opacity= 0.8
                                     )
                        ),
                        go.Scatter(
                                x=tx_graph.query("Segment == 'Mid-Value'")['Frequency'],
                                y=tx_graph.query("Segment == 'Mid-Value'")['Revenue'],
                                mode='markers',
                                name='Mid',
                                marker= dict(size= 9,
                                             line= dict(width=1),
                                             color= 'green',
                                             opacity= 0.5
                                             )
                                ),
                                go.Scatter(
                                        x=tx_graph.query("Segment == 'High-Value'")['Frequency'],
                                        y=tx_graph.query("Segment == 'High-Value'")['Revenue'],
                                        mode='markers',
                                        name='High',
                                        marker= dict(size= 11,
                                                     line= dict(width=1),
                                                     color= 'red',
                                                     opacity= 0.9
                                                     )
                                        ),
                                        ]
        
        plot_layout = go.Layout(
                yaxis= {'title': "Revenue"},
                xaxis= {'title': "Frequency"},
                title='Segments'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./segment/revfresegments.png')
        
        tx_graph = tx_user.query("Revenue < 50000 and Frequency < 2000")
                
        plot_data = [
                go.Scatter(
                        x=tx_graph.query("Segment == 'Low-Value'")['Recency'],
                        y=tx_graph.query("Segment == 'Low-Value'")['Revenue'],
                        mode='markers',
                        name='Low',
                        marker= dict(size= 7,
                                     line= dict(width=1),
                                     color= 'blue',
                                     opacity= 0.8
                                     )
                        ),
                        go.Scatter(
                                x=tx_graph.query("Segment == 'Mid-Value'")['Recency'],
                                y=tx_graph.query("Segment == 'Mid-Value'")['Revenue'],
                                mode='markers',
                                name='Mid',
                                marker= dict(size= 9,
                                             line= dict(width=1),
                                             color= 'green',
                                             opacity= 0.5
                                             )
                                ),
                                go.Scatter(
                                        x=tx_graph.query("Segment == 'High-Value'")['Recency'],
                                        y=tx_graph.query("Segment == 'High-Value'")['Revenue'],
                                        mode='markers',
                                        name='High',
                                        marker= dict(size= 11,
                                                     line= dict(width=1),
                                                     color= 'red',
                                                     opacity= 0.9
                                                     )
                                        ),
                                        ]
        
        plot_layout = go.Layout(
                yaxis= {'title': "Revenue"},
                xaxis= {'title': "Recency"},
                title='Segments'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./segment/revrecsegments.png')
        
        ''' #freuency vs recency segmentation
        '''
        
        tx_graph = tx_user.query("Revenue < 50000 and Frequency < 2000")
        
        plot_data = [
                go.Scatter(
                        x=tx_graph.query("Segment == 'Low-Value'")['Recency'],
                        y=tx_graph.query("Segment == 'Low-Value'")['Frequency'],
                        mode='markers',
                        name='Low',
                        marker= dict(size= 7,
                                     line= dict(width=1),
                                     color= 'blue',
                                     opacity= 0.8
                                     )
                        ),
                        go.Scatter(
                                x=tx_graph.query("Segment == 'Mid-Value'")['Recency'],
                                y=tx_graph.query("Segment == 'Mid-Value'")['Frequency'],
                                mode='markers',
                                name='Mid',
                                marker= dict(size= 9,
                                             line= dict(width=1),
                                             color= 'green',
                                             opacity= 0.5
                                             )
                                ),
                                go.Scatter(
                                        x=tx_graph.query("Segment == 'High-Value'")['Recency'],
                                        y=tx_graph.query("Segment == 'High-Value'")['Frequency'],
                                        mode='markers',
                                        name='High',
                                        marker= dict(size= 11,
                                                     line= dict(width=1),
                                                     color= 'red',
                                                     opacity= 0.9
                                                     )
                                        ),
                                        ]
        
        plot_layout = go.Layout(
                yaxis= {'title': "Frequency"},
                xaxis= {'title': "Recency"},
                title='Segments'
                )
        fig = go.Figure(data=plot_data, layout=plot_layout)
        fig.write_image('./segment/frerecsegments.png')
        
        
        
        #end of Customer segmentation
    
        
        bload = ttk.Button(self, text="next", command=lambda: controller.show_frame(PageOne))
        bload.pack()
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        label = tk.Label(self, text="Load Data", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        tk.Label(self, text='File Path').pack()
        global v
        v = tk.StringVar()
        entry = ttk.Entry(self, textvariable=v).pack()
        button = ttk.Button(self, text="Browse Data", command= self.import_csv_data(controller))
        button.pack()
        #but2 = ttk.Button(self, text=")



class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command=lambda: controller.show_frame(Revenue))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command=lambda: controller.show_frame(MGR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command=lambda: controller.show_frame(MAC))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="MOnthly Order Count", command=lambda: controller.show_frame(MOC))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=lambda: controller.show_frame(ARPO))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command=lambda: controller.show_frame(NCR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        
        
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)

        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = lambda: controller.show_frame(Recency))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = lambda: controller.show_frame(Frequency))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = lambda: controller.show_frame(Monetary))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = lambda: controller.show_frame(RevFreSegments))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = lambda: controller.show_frame(RevRecSegments))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = lambda: controller.show_frame(FreRecSegments))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
        
        
class Recency(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = showgr(frame2, "Recency", "./segment/recency.png"))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = lambda: controller.show_frame(Frequency))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = lambda: controller.show_frame(Monetary))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = lambda: controller.show_frame(RevFreSegments))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = lambda: controller.show_frame(RevRecSegments))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = lambda: controller.show_frame(FreRecSegments))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
class Frequency(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = lambda: controller.show_frame(Recency))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = showgr(frame2, "Frequency", "./segment/frequency.png"))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = lambda: controller.show_frame(Monetary))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = lambda: controller.show_frame(RevFreSegments))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = lambda: controller.show_frame(RevRecSegments))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = lambda: controller.show_frame(FreRecSegments))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
class Monetary(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = lambda: controller.show_frame(Recency))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = lambda: controller.show_frame(Frequency))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = showgr(frame2,"Monetary", "./segment/monetary.png"))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = lambda: controller.show_frame(RevFreSegments))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = lambda: controller.show_frame(RevRecSegments))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = lambda: controller.show_frame(FreRecSegments))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
class RevFreSegments(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = lambda: controller.show_frame(Recency))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = lambda: controller.show_frame(Frequency))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = lambda: controller.show_frame(Monetary))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = showgr(frame2,"Revenue vs Frequency Segments", "./segment/revfresegments.png"))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = lambda: controller.show_frame(RevRecSegments))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = lambda: controller.show_frame(FreRecSegments))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
        
class RevRecSegments(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = lambda: controller.show_frame(Recency))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = lambda: controller.show_frame(Frequency))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = lambda: controller.show_frame(Monetary))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = lambda: controller.show_frame(RevFreSegments))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = showgr(frame2,"Revenue vs Recency Segments", "./segment/revrecsegments.png"))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = lambda: controller.show_frame(FreRecSegments))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
class FreRecSegments(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Segmentation", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        button2 = ttk.Button(frame, text="Go back", command =  lambda: controller.show_frame(PageOne))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button3 = ttk.Button(frame, text="Recency", command = lambda: controller.show_frame(Recency))
        button3.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button4 = ttk.Button(frame, text="Frequency", command = lambda: controller.show_frame(Frequency))
        button4.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button5 = ttk.Button(frame, text="Monetary", command = lambda: controller.show_frame(Monetary))
        button5.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button6 = ttk.Button(frame, text="Revenue vs Frequency Segments", command = lambda: controller.show_frame(RevFreSegments))
        button6.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button7 = ttk.Button(frame, text="Revenue vs Recency Segments", command = lambda: controller.show_frame(RevRecSegments))
        button7.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        button8 = ttk.Button(frame, text="Frequency vs Recency Segments", command = showgr(frame2,"Frequency vs Recency Segments", "./segment/frerecsegments.png"))
        button8.pack(side = TOP, anchor = E, fill = X, expand = TRUE)
        
        
class Revenue(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command= showgr(frame2,"Monthly Revenue", "./stats/revenue.png"))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command=lambda: controller.show_frame(MGR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command=lambda: controller.show_frame(MAC))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="MOnthly Order Count", command=lambda: controller.show_frame(MOC))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=lambda: controller.show_frame(ARPO))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command=lambda: controller.show_frame(NCR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
                
class MGR(tk.Frame): #monthly growth rate
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command= lambda: controller.show_frame(Revenue))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command= showgr(frame2,"Monthly Growth Rate", "./stats/mgr.png"))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command=lambda: controller.show_frame(MAC))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="MOnthly Order Count", command=lambda: controller.show_frame(MOC))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=lambda: controller.show_frame(ARPO))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command=lambda: controller.show_frame(NCR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
    
class MAC(tk.Frame): #monthly Active Customer
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command= lambda: controller.show_frame(Revenue))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command=lambda: controller.show_frame(MGR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command= showgr(frame2,"Monthly Active Customer", "./stats/mac.png"))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="MOnthly Order Count", command=lambda: controller.show_frame(MOC))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=lambda: controller.show_frame(ARPO))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command=lambda: controller.show_frame(NCR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)

class MOC(tk.Frame): #monthly order count
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command= lambda: controller.show_frame(Revenue))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command=lambda: controller.show_frame(MGR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command=lambda: controller.show_frame(MAC))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Order Count", command= showgr(frame2,"Monthly Order Count", "./stats/moc.png"))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=lambda: controller.show_frame(ARPO))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command=lambda: controller.show_frame(NCR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)

class ARPO(tk.Frame): #Average Revenue per Order
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command= lambda: controller.show_frame(Revenue))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command=lambda: controller.show_frame(MGR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command=lambda: controller.show_frame(MAC))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="MOnthly Order Count", command=lambda: controller.show_frame(MOC))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=showgr(frame2,"Average Revenue per Order", "./stats/arpo.png"))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command=lambda: controller.show_frame(NCR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)

class NCR(tk.Frame): #New Customer Ratio
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Stats", font=LARGE_FONT)
        label.pack(pady=20, padx=20)
        button1 = ttk.Button(self, text="Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text="Segmentation", command=lambda: controller.show_frame(PageTwo))
        button2.pack()
        
        frame2 = tk.Frame(self, height = 100, bg="BLACK", borderwidth= 2)
        frame2.pack(side= RIGHT, fill = BOTH)
        def showgr(fr,label,name):
            label = tk.Label(fr, text=label, font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            load = Image.open(name)
            render = ImageTk. PhotoImage(load)
            img = tk.Button(fr, image = render)
            img.image = render
            img.pack()
        
        frame = tk.Frame(self, height = 100, width =50, borderwidth= 2)
        frame.pack(side=LEFT, fill = BOTH)
        '''Revenue, MGR, MAC,MOC, ARPO, NCR)'''
        button3 = ttk.Button(frame, text="Monthly Revenue", command= lambda: controller.show_frame(Revenue))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="Monthly Growth Rate", command=lambda: controller.show_frame(MGR))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button3 = ttk.Button(frame, text="Monthly Active Customer", command=lambda: controller.show_frame(MAC))
        button3.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        
        button2 = ttk.Button(frame, text="MOnthly Order Count", command=lambda: controller.show_frame(MOC))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="Average Revenue per Order", command=lambda: controller.show_frame(ARPO))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        button2 = ttk.Button(frame, text="New Customer Ratio", command= showgr(frame2,"New Customer Ratio", "./stats/ncr.png"))
        button2.pack(side = TOP, anchor = E,fill = X, expand = TRUE)
        


app = Customer()
app.mainloop()