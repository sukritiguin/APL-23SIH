from django.shortcuts import render
from django.http import HttpResponse

import plotly.graph_objects as go
from datetime import datetime, timedelta

from django.shortcuts import render
import plotly.graph_objects as go
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


import random

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