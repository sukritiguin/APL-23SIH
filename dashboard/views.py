from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import time

import plotly.graph_objects as go
from datetime import datetime, timedelta

from django.shortcuts import render
import plotly.graph_objects as go
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.safestring import mark_safe

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import random
import os
import boto3
import pandas as pd

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from io import BytesIO
import os
import glob




def delete_files_in_folder(folder):
    files = glob.glob(os.path.join(folder, '*'))
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

def generate_power_consumption_plot(df_specific_day, specific_day):
    # Convert the 'Time' column to a string representation
    df_specific_day = df_specific_day.copy()
    df_specific_day['Time'] = df_specific_day['Time'].astype(str)

    # Create a bar graph for the specific day
    plt.figure(figsize=(12, 6))
    plt.bar(df_specific_day['Time'], df_specific_day['Power Consumed'])
    plt.title(f'Power Consumption on {specific_day}')
    plt.xlabel('Time (hours)')
    plt.ylabel('Power Consumed')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better visibility
    plt.tight_layout()

    # Save the plot as an image
    # Specify the image folder
    img_folder = os.path.join(os.path.dirname(__file__), 'img')

    # Ensure the img folder exists, create it if not
    os.makedirs(img_folder, exist_ok=True)

    # Specify the plot filename with the correct path
    temp = str(specific_day).replace(':', '_')
    plot_filename = os.path.join(img_folder, f'plot_data{temp}.png')

    plt.savefig(plot_filename, format='png', bbox_inches='tight')
    plt.close()

    # Convert the plot image to an inline image
    img = Image(plot_filename, width=480, height=240)

    # Return the inline image
    return img

# Set the seed for reproducibility
# np.random.seed(42)

def generateReport(df):
    # Create a PDF file
    pdf_filename = 'output.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Get predefined styles from the sample style sheet
    styles = getSampleStyleSheet()

    # Define your custom styles for header and text
    header_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.blue
    )

    text_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=12,
        space_after=5
    )

    # Add header
    header = Paragraph("Power Consumption Report", style=header_style)
    desc = "Our project solution aims at achieving an automated public lighting system through IOT with innovative circuitry that will not only reduce energy costs and expenses but also have a feature for fault detection. Along with a robust software system that stores, comprising of a database that will store all data regarding power consumption, saving and history of usage and a fluid and user-friendly Graphical User Interface for visualisation of such data, which will enable operators to see how many units of power is saved and also notify them about faulty lamps in the zone and help them identify the pin-point location of any faulty lamps."
    text = Paragraph(
        desc,
        style=text_style)

    # Convert DataFrame to table
    table_data = [df.columns] + df.values.tolist()

    # Define the style for the table
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]

    # Alternating row colors
    for i in range(1, len(df), 2):
        style.extend([
            ('BACKGROUND', (0, i), (-1, i), colors.lightgreen),
            ('BACKGROUND', (0, i + 1), (-1, i + 1), colors.lightblue),
        ])
    col_widths = [max([len(str(row[i])) for row in table_data]) * 12 for i in range(len(df.columns))]
    tbl = Table(table_data, style=style, colWidths=col_widths * len(df.columns))

    # Create story and add elements
    story = [header, text, Spacer(1, 12), tbl]

    # Add plots for each day to the PDF
    for specific_day in pd.date_range(start='2023-01-01', periods=30, freq='D'):
        df_specific_day = df[df['Day'] == specific_day]
        plot = generate_power_consumption_plot(df_specific_day, str(specific_day))
        story.append(plot)

    # Build the PDF
    doc.build(story)
    delete_files_in_folder('img')


def fetchDataFromAWSDynamoDB():
    from datetime import datetime
    # Replace these values with your own
    aws_access_key_id = 'AKIAWHBWMPR3QJWWSFWS'
    aws_secret_access_key = 'dSFhG50Rgqigd5/KWObts2czhwgkFygbw9BMbqyc'
    region_name = 'ap-southeast-1'
    table_name = 'SIH_FINAL_table'

    # Create a DynamoDB resource
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    # Get a reference to the table
    table = dynamodb.Table(table_name)

    # Use the `scan` method to fetch all items in the table
    response = table.scan()
    return response


def getCurrentDF():
    response = fetchDataFromAWSDynamoDB()
    datalist = response['Items']
    df = pd.DataFrame(datalist)
    # Remove the newline character from 'TimeStamp'
    df['TimeStamp'] = df['TimeStamp'].str.strip()

    # Convert the 'TimeStamp' column to timestamps
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format="%a %b %d %H:%M:%S %Y", errors='coerce')
    
    df = df[['TS', 'TimeStamp', 'Current', 'Voltage']]
    # Convert the 'Light' column to integers
    # df['Light'] = df['Light'].astype(int)
    df['Current'] = df['Current'].astype(float)
    df['Voltage'] = df['Voltage'].astype(float)
    # Calculate the power and create a new 'Power' column
    df['Power'] = df['Current'] * df['Voltage']
    return df

def getPlotData():
    response = fetchDataFromAWSDynamoDB()
    datalist = response['Items']
    df = pd.DataFrame(datalist)
    # Remove the newline character from 'TimeStamp'
    df['TimeStamp'] = df['TimeStamp'].str.strip()

    # Convert the 'TimeStamp' column to timestamps
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format="%a %b %d %H:%M:%S %Y", errors='coerce')
    
    df = df[['TS', 'TimeStamp', 'Current', 'Voltage']]
    # Convert the 'Light' column to integers
    # df['Light'] = df['Light'].astype(int)
    df['Current'] = df['Current'].astype(float)
    df['Voltage'] = df['Voltage'].astype(float)
    # Calculate the power and create a new 'Power' column
    df['Power'] = df['Current'] * df['Voltage']
    print(df)
    result_df = df.groupby(pd.Grouper(key='TimeStamp', freq='1S')).agg({'Power': 'sum'}).reset_index()

    
    return list(result_df['TimeStamp']), list(result_df['Power'])
    

@login_required
def plotly_graph(request):
    if not request.user.is_authenticated:
        # Redirect to the home page if the user is not logged in
        return redirect('login')  # Adjust the 'home' URL to match your home page URL



    # Sample data
    # days = 10
    # start_date = datetime(2023, 1, 1)
    # date_list = [start_date + timedelta(days=x) for x in range(days)]
    # values = [10, 12, 8, 15, 11, 14, 9, 13, 16, 10]

    date_list, values = getPlotData()

    # Get user input from the form or use default values
    selected_start_date = request.GET.get('start_date', date_list[0].strftime('%Y-%m-%d'))
    selected_end_date = request.GET.get('end_date', date_list[-1].strftime('%Y-%m-%d'))

    # Convert input strings to datetime objects
    start_date_obj = datetime.strptime(selected_start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(selected_end_date, '%Y-%m-%d')

    # Filter data based on user input
    # filtered_dates = [date for date in date_list if start_date_obj <= date <= end_date_obj]
    # filtered_values = [values[i] for i, date in enumerate(date_list) if start_date_obj <= date <= end_date_obj]
    filtered_dates = [date for date in date_list]
    filtered_values = [values[i] for i, date in enumerate(date_list)]

    # Create a trace
    trace = go.Scatter(x=filtered_dates, y=filtered_values, mode='lines+markers', name='Filtered Values')

    # Create layout with transparent background and white labels
    layout = go.Layout(
        title='Filtered Day-by-Day Graph',
        titlefont=dict(color='white'),
        xaxis=dict(title='Date', tickfont=dict(color='white')),
        yaxis=dict(title='Values', tickfont=dict(color='white')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Create figure
    fig = go.Figure(data=[trace], layout=layout)

    # Convert the figure to HTML
    plot_div = fig.to_html(full_html=False)

    context = {
        'plot_div': plot_div,
        'start_date': selected_start_date,
        'end_date': selected_end_date,
    }

    return render(request, 'dashboard/index.html', context)


def generate_plot(title, x_values, y_values, y_axis_title):
    trace = go.Scatter(x=x_values, y=y_values, mode='lines+markers', name=y_axis_title)
    layout = go.Layout(
        title=title,
        titlefont=dict(color='white'),
        xaxis=dict(title='Time', tickfont=dict(color='white')),
        yaxis=dict(
            title=y_axis_title,
            tickfont=dict(color='white'),
            range=[0, 10]  # Set fixed range for y-axis
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig = go.Figure(data=[trace], layout=layout)
    plot_div = fig.to_html(full_html=False)
    return plot_div

# def generate_plot(title, x_values, y_values, y_axis_title):
#     trace = go.Scatter(x=x_values, y=y_values, mode='lines+markers', name=y_axis_title)
#     layout = go.Layout(
#         title=title,
#         titlefont=dict(color='white'),
#         xaxis=dict(title='Time', tickfont=dict(color='white')),
#         yaxis=dict(
#             title=y_axis_title,
#             tickfont=dict(color='white'),
#             range=[0, 10]  # Set fixed range for y-axis
#         ),
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)'
#     )
#     fig = go.Figure(data=[trace], layout=layout)
#     plot_div = fig.to_html(full_html=False)
#     return plot_div



@login_required
def plot_voltage(request):
    # Get the current time
    now = datetime.now()

    # Sample data for the last 30 seconds
    df = getCurrentDF()
    time_interval = 30  # seconds
    time_points = [now - timedelta(seconds=i) for i in range(time_interval)][::-1]
    time_points = list(df['TimeStamp'])
    voltage_values = [random.uniform(0, 5) for _ in range(time_interval)]
    voltage_values = list(df['Voltage'])

    # print(time_points)
    # print(type(time_points))

    # ind = 0
    # t_points = []
    # while ind < len(time_points):
    #     t_points += time_points[ind]
    #     ind += 4

    # time_points = t_points[-30:]
    time_points = time_points[-30:]

    v_points = []
    ind = 0
    while ind < len(voltage_values):
        v_points.append(voltage_values[ind])
        ind += 4

    voltage_values = v_points[-30:]


    print(time_points)
    print(voltage_values)



    # Create a trace
    trace = go.Scatter(x=time_points, y=voltage_values, mode='lines+markers', name='Voltage')

    # Create layout with transparent background and white labels
    layout = go.Layout(
        title='Voltage vs. Time (Last 30 Seconds)',
        titlefont=dict(color='white'),
        xaxis=dict(title='Time', tickfont=dict(color='white')),
                yaxis=dict(
            title='Voltage',
            tickfont=dict(color='white'),
            range=[0, 2]  # Set fixed range for y-axis
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Create figure
    fig = go.Figure(data=[trace], layout=layout)

    # Convert the figure to HTML
    plot_div = fig.to_html(full_html=False)

    context = {
        'volt_plot_div': plot_div,
    }

    return render(request, 'dashboard/voltage_analysis.html', context)


@login_required
def plot_current(request):
    # Get the current time
    now = datetime.now()

    # Sample data for the last 30 seconds
    time_interval = 30  # seconds
    time_points = [now - timedelta(seconds=i) for i in range(time_interval)][::-1]
    voltage_values = [random.uniform(0, 5) for _ in range(time_interval)]


    df = getCurrentDF()
    time_interval = 30  # seconds
    time_points = [now - timedelta(seconds=i) for i in range(time_interval)][::-1]
    time_points = list(df['TimeStamp'])
    voltage_values = [random.uniform(0, 5) for _ in range(time_interval)]
    voltage_values = list(df['Current'])

    time_points = time_points[-30:]

    v_points = []
    ind = 0
    while ind < len(voltage_values):
        v_points.append(voltage_values[ind])
        ind += 4

    voltage_values = v_points[-30:]
    print(time_points)
    print(voltage_values)
    
    # Create a trace
    trace = go.Scatter(x=time_points, y=voltage_values, mode='lines+markers', name='Voltage')

    # Create layout with transparent background and white labels
    layout = go.Layout(
        title='Current vs. Time (Last 30 Seconds)',
        titlefont=dict(color='white'),
        xaxis=dict(title='Time', tickfont=dict(color='white')),
                yaxis=dict(
            title='Current',
            tickfont=dict(color='white'),
            range=[0, 2]  # Set fixed range for y-axis
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Create figure
    fig = go.Figure(data=[trace], layout=layout)

    # Convert the figure to HTML
    plot_div = fig.to_html(full_html=False)

    context = {
        'current_plot_div': plot_div,
    }

    return render(request, 'dashboard/current_analysis.html', context)
    # return JsonResponse({'current_plot_div': plot_div})


@login_required
def plot_voltage_current_analysis(request):
    # Get the current time
    now = datetime.now()

    # Sample data for the last 30 seconds
    time_interval = 30  # seconds
    time_points = [now - timedelta(seconds=i) for i in range(time_interval)][::-1]
    voltage_values = [random.uniform(0, 5) for _ in range(time_interval)]

    # Generate HTML representation for voltage plot
    voltage_plot_div = generate_plot('Voltage vs. Time (Last 30 Seconds)', time_points, voltage_values, 'Voltage')

    # Sample data for current vs. time
    current_values = [random.uniform(0, 10) for _ in range(time_interval)]

    # Generate HTML representation for current plot
    current_plot_div = generate_plot('Current vs. Time (Last 30 Seconds)', time_points, current_values, 'Current')

    # Render the HTML template with both plots
    # return render(request, 'dashboard/voltage_graph.html', {'volt_plot_div': voltage_plot_div, 'current_plot_div': current_plot_div})

    # Return JSON response with the plot divs
    response_data = {
        'volt_plot_div': mark_safe(voltage_plot_div),
        'current_plot_div': mark_safe(current_plot_div),
    }

    return JsonResponse(response_data, content_type='application/json')


    
    # response_data = {
    #     'voltage_data': {
    #         'time_points': time_points,
    #         'values': voltage_values,
    #         'title': 'Voltage vs. Time (Last 30 Seconds)',
    #         'y_axis_title': 'Voltage',
    #     },
    #     'current_data': {
    #         'time_points': time_points,
    #         'values': current_values,
    #         'title': 'Current vs. Time (Last 30 Seconds)',
    #         'y_axis_title': 'Current',
    #     },
    # }

    # return JsonResponse(response_data)

@login_required
def plot_voltage2(request):
    # Get the current time
    now = datetime.now()

    # Sample data for the last 30 seconds
    time_interval = 30  # seconds
    time_points = [now - timedelta(seconds=i) for i in range(time_interval)][::-1]
    voltage_values = [random.uniform(0, 5) for _ in range(time_interval)]

    # Create a trace
    trace = go.Scatter(x=time_points, y=voltage_values, mode='lines+markers', name='Voltage')

    # Create layout with transparent background and white labels
    layout = go.Layout(
        title='Voltage vs. Time (Last 30 Seconds)',
        titlefont=dict(color='white'),
        xaxis=dict(title='Time', tickfont=dict(color='white')),
                yaxis=dict(
            title='Voltage',
            tickfont=dict(color='white'),
            range=[0, 7]  # Set fixed range for y-axis
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Create figure
    fig = go.Figure(data=[trace], layout=layout)

    # Convert the figure to HTML
    plot_div = fig.to_html(full_html=False)

    context = {
        'volt_plot_div': plot_div,
    }

    return render(request, 'dashboard/voltage_graph.html', context)


# def plotly_graph(request):
#     # Sample data
#     days = 10
#     start_date = datetime(2023, 1, 1)
#     date_list = [start_date + timedelta(days=x) for x in range(days)]
#     values = [10, 12, 8, 15, 11, 14, 9, 13, 16, 10]

#     # Create a trace
#     trace = go.Scatter(x=date_list, y=values, mode='lines+markers', name='Daily Values')

#     # Create layout with transparent background
#     layout = go.Layout(
#         title='Day-by-Day Graph',
#         titlefont=dict(color='white'),  # Set the title color to white
#         xaxis=dict(title='Date', tickfont=dict(color='white'), titlefont=dict(color='white')),
#         yaxis=dict(title='Values', tickfont=dict(color='white'), titlefont=dict(color='white')),
#         plot_bgcolor='rgba(0,0,0,0)',
#         paper_bgcolor='rgba(0,0,0,0)'
#     )
#     # Create figure
#     fig = go.Figure(data=[trace], layout=layout)

#     # Convert the figure to HTML
#     plot_div = fig.to_html(full_html=False)

#     return render(request, 'dashboard/index.html', {'plot_div': plot_div})


# Create your views here.
# def dashboard_view(request):
#     context = {}
#     return render(request, 'dashboard/index.html', context)

def home_view(request):
    context = {}
    return render(request, 'dashboard/home.html', context)

def aboutus_view(request):
    context = {}
    return render(request, 'dashboard/aboutus.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')  # Redirect to your home or dashboard page
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')




def createPDFReport(df):
    fig, ax = plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')

    pp = PdfPages("table.pdf")
    pp.savefig(fig, bbox_inches='tight')
    pp.close()

def send_mail(receiver_email, subject, body, filenames=None):
    sender_email = "2811guin@gmail.com"
    password = os.environ.get('GOOGLE_GMAIL_AUTH_PASS')

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))



    # Attach multiple files
    if filenames:
        for filename in filenames:
            # Open the file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as an attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(filename)}",
            )

            # Add attachment to message
            message.attach(part)

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)




def send_report_email(request):
    # Generate random data for 30 days
    days = pd.date_range(start='2023-01-01', periods=30, freq='D')
    times = pd.date_range(start='2023-01-01', periods=24, freq='H').time
    power_consumed = np.random.uniform(low=10, high=100, size=(30, 24))

    # Flatten the 2D array to create a single column for power consumed
    power_consumed_flat = power_consumed.flatten()

    # Create the DataFrame
    data = {'Day': np.repeat(days, 24),
            'Time': np.tile(times, 30),
            'Power Consumed': power_consumed_flat}

    df = pd.DataFrame(data)

    generateReport(df)
    df.to_csv("table.csv", index=False)
    if request.method == 'POST':
        email = request.POST.get('email', '')

        # Add your logic to generate the report or use an existing report
        # For example, you might want to use Django's render_to_string to render an HTML template as the email body.


        
        
        # Send the email
        send_mail(
            receiver_email=email,
            subject="Attachment is awesome",
            body="Email sent successfully thought dashboard",
            filenames=[r'output.pdf', r'table.csv']
        )

        # Add a success message
        messages.success(request, 'Email sent successfully!')

        return redirect('dashboard')  # Redirect to the dashboard or any other desired page
    else:
        return render(request, 'dashboard/index.html')  # Render your template as usual