from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

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

@login_required
def plotly_graph(request):
    if not request.user.is_authenticated:
        # Redirect to the home page if the user is not logged in
        return redirect('login')  # Adjust the 'home' URL to match your home page URL



    # Sample data
    days = 10
    start_date = datetime(2023, 1, 1)
    date_list = [start_date + timedelta(days=x) for x in range(days)]
    values = [10, 12, 8, 15, 11, 14, 9, 13, 16, 10]

    # Get user input from the form or use default values
    selected_start_date = request.GET.get('start_date', date_list[0].strftime('%Y-%m-%d'))
    selected_end_date = request.GET.get('end_date', date_list[-1].strftime('%Y-%m-%d'))

    # Convert input strings to datetime objects
    start_date_obj = datetime.strptime(selected_start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(selected_end_date, '%Y-%m-%d')

    # Filter data based on user input
    filtered_dates = [date for date in date_list if start_date_obj <= date <= end_date_obj]
    filtered_values = [values[i] for i, date in enumerate(date_list) if start_date_obj <= date <= end_date_obj]

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

    return render(request, 'dashboard/voltage_analysis.html', context)


@login_required
def plot_current(request):
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
        title='Current vs. Time (Last 30 Seconds)',
        titlefont=dict(color='white'),
        xaxis=dict(title='Time', tickfont=dict(color='white')),
                yaxis=dict(
            title='Current',
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


def send_mail(receiver_email, subject, body, filename=""):
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

    if filename != "":
        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)




def send_report_email(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        # Add your logic to generate the report or use an existing report
        # For example, you might want to use Django's render_to_string to render an HTML template as the email body.

        # Send the email
        send_mail(
            receiver_email=email,
            subject="Trying to communicate",
            body="Email sent successfully thought dashboard"
        )

        # Add a success message
        messages.success(request, 'Email sent successfully!')

        return redirect('dashboard')  # Redirect to the dashboard or any other desired page
    else:
        return render(request, 'dashboard/index.html')  # Render your template as usual