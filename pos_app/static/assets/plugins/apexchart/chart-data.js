'use strict';

$(document).ready(function () {

  function generateData(baseval, count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
      var x = Math.floor(Math.random() * (750 - 1 + 1)) + 1;;
      var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
      var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;

      series.push([x, y, z]);
      baseval += 86400000;
      i++;
    }
    return series;
  }


  // Column chart
  if ($('#sales_chart').length > 0) {
    var columnCtx = document.getElementById("sales_chart"),
      columnConfig = {
        colors: ['#7638ff', '#fda600'],
        series: [
          {
            name: "Received",
            type: "column",
            data: [70, 150, 80, 180, 150, 175, 201, 60, 200, 120, 190, 160, 50]
          },
          {
            name: "Pending",
            type: "column",
            data: [23, 42, 35, 27, 43, 22, 17, 31, 22, 22, 12, 16, 80]
          }
        ],
        chart: {
          type: 'bar',
          fontFamily: 'Roboto, sans-serif',
          height: 350,
          toolbar: {
            show: false
          }
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '60%',
            endingShape: 'rounded'
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        xaxis: {
          categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
        },
        yaxis: {
          title: {
            text: '$ (thousands)'
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return "$ " + val + " thousands"
            }
          }
        }
      };
    var columnChart = new ApexCharts(columnCtx, columnConfig);
    columnChart.render();
  }


  if ($('#reservation-chart').length > 0) {
    var sCol = {
        chart: {
            width: '100%',
            height: 'auto', // Adjusts dynamically
            type: 'bar',
            toolbar: { show: false },
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '80%', // Adjust spacing
                endingShape: 'rounded'
            }
        },
        colors: ['#D0E3E6', '#4361ee'],
        states: {
            hover: {
                filter: {
                    type: 'darken',
                    value: 0.3
                }
            }
        },
        dataLabels: { enabled: false },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
        },
        series: [{
            name: 'Net Profit',
            data: [7, 9, 4, 9, 6, 8, 10]
        }],
        fill: { opacity: 1 },
        xaxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'July'],
            labels: { show: false },
            axisTicks: { show: false },
            axisBorder: { show: false }
        },
        grid: {
            show: false, // Hides grid lines
            padding: { left: 0, right: 0, top: 0, bottom: 0 }
        },
        yaxis: { labels: { show: false } },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val;
                }
            }
        }
    };

    var chart = new ApexCharts(
        document.querySelector("#reservation-chart"),
        sCol
    );

    chart.render();
  }

  //Report Chart
  if ($('#report_chart').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        width: 70,
        height: 46,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#7539FF'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };




    var chart = new ApexCharts(document.querySelector("#report_chart"), options);
    chart.render();
  }
  if ($('#report_chart_2').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        width: 70,
        height: 50,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#27AE60'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };


    var chart = new ApexCharts(document.querySelector("#report_chart_2"), options);
    chart.render();
  }
  if ($('#report_chart_3').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        width: 70,
        height: 50,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#E2B93B'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };

    var chart = new ApexCharts(document.querySelector("#report_chart_3"), options);
    chart.render();
  }
  if ($('#report_chart_4').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        width: 70,
        height: 50,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#EF1E1E'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };

    var chart = new ApexCharts(document.querySelector("#report_chart_4"), options);
    chart.render();
  }
  //Payment Report Chart
  if ($('#payment_report_chart').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        height: 46,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#7539FF'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };




    var chart = new ApexCharts(document.querySelector("#payment_report_chart"), options);
    chart.render();
  }
  if ($('#payment_report_chart_2').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        height: 50,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#27AE60'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };




    var chart = new ApexCharts(document.querySelector("#payment_report_chart_2"), options);
    chart.render();
  }
  if ($('#payment_report_chart_3').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        height: 50,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#E2B93B'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };

    var chart = new ApexCharts(document.querySelector("#payment_report_chart_3"), options);
    chart.render();
  }
  if ($('#payment_report_chart_4').length > 0) {
    var options = {
      series: [{
        data: [0, 6, 24, 14, 20, 15, 37]
      }],
      chart: {
        type: 'area',
        height: 50,
        sparkline: {
          enabled: true
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      colors: ['#EF1E1E'],

      tooltip: {
        fixed: {
          enabled: false
        },
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      }
    };

    var chart = new ApexCharts(document.querySelector("#payment_report_chart_4"), options);
    chart.render();
  }
  //Pie Chart
  if ($('#invoice_chart').length > 0) {
    var pieCtx = document.getElementById("invoice_chart"),
      pieConfig = {
        colors: ['#03C95A', '#E70D0D', '#AB47BC', '#FFC107'],
        series: [45, 15, 21, 5],
        chart: {
          fontFamily: 'Roboto, sans-serif',
          height: 150,
          type: 'donut',
          offsetX: -30,
        },
        labels: ['Paid', 'Overdue', 'Pending', 'Draft'],
        legend: { show: true },
        dataLabels: {
          enabled: false // Disable the data labels
        },
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true,
                name: {
                  show: true,
                  fontSize: '2px',
                },
                value: {
                  show: true,
                  fontSize: '12px',
                  formatter: function (val) {
                    return val + "%";
                  }
                },
                total: {
                  show: true,
                  showAlways: true,
                  formatter: function (w) {
                    return w.globals.seriesTotals.reduce((a, b) => {
                      return 45;
                    }, 0);
                  },
                  label: 'Paid'
                }
              }
            }
          }
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 300
            },
            legend: {
              position: 'right'
            }
          }
        }]
      };
    var pieChart = new ApexCharts(pieCtx, pieConfig);
    pieChart.render();
  }


  // Simple Line
  if ($('#s-line').length > 0) {
    var sline = {
      chart: {
        height: 350,
        type: 'line',
        zoom: {
          enabled: false
        },
        toolbar: {
          show: false,
        }
      },
      colors: ['#3550DC'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'straight'
      },
      series: [{
        name: "Desktops",
        data: [10, 41, 35, 51, 49, 62, 69, 91, 148]
      }],
      title: {
        text: 'Product Trends by Month',
        align: 'left'
      },
      grid: {
        row: {
          colors: ['#f1f2f3', 'transparent'], // takes an array which will be repeated on columns
          opacity: 0.5
        },
      },
      xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#s-line"),
      sline
    );

    chart.render();
  }


  // Simple Line Area
  if ($('#s-line-area').length > 0) {
    var sLineArea = {
      chart: {
        height: 350,
        type: 'area',
        toolbar: {
          show: false,
        }
      },
      colors: ['#3550DC', '#888ea8'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth'
      },
      series: [{
        name: 'series1',
        data: [31, 40, 28, 51, 42, 109, 100]
      }, {
        name: 'series2',
        data: [11, 32, 45, 32, 34, 52, 41]
      }],

      xaxis: {
        type: 'datetime',
        categories: ["2018-09-19T00:00:00", "2018-09-19T01:30:00", "2018-09-19T02:30:00", "2018-09-19T03:30:00", "2018-09-19T04:30:00", "2018-09-19T05:30:00", "2018-09-19T06:30:00"],
      },
      tooltip: {
        x: {
          format: 'dd/MM/yy HH:mm'
        },
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#s-line-area"),
      sLineArea
    );

    chart.render();
  }

  if ($('#s-col').length > 0) {
    var sCol = {
      chart: {
        height: 290,
        type: 'bar',
        toolbar: {
          show: false,
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '80%',
          borderRadius: 5,
          endingShape: 'rounded', // This rounds the top edges of the bars
        },
      },
      colors: ['#FFAD6A', '#5777E6', '#5CC583'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: true,
        width: 2,
        colors: ['transparent']
      },

      series: [{
        name: 'Inprogress',
        data: [19, 65, 19, 19, 19, 19, 19]
      }, {
        name: 'Active',
        data: [89, 45, 89, 46, 61, 25, 79]
      },
      {
        name: 'Completed',
        data: [39, 39, 39, 80, 48, 48, 48]
      }],
      xaxis: {
        categories: ['15 Jan', '16 Jan', '17 Jan', '18 Jan', '19 Jan', '20 Jan', '21 Jan'],
        labels: {
          style: {
            colors: '#0C1C29',
            fontSize: '12px',
          }
        }
      },
      yaxis: {
        labels: {
          offsetX: -15,
          style: {
            colors: '#6D777F',
            fontSize: '14px',
          }
        }
      },
      grid: {
        borderColor: '#CED2D4',
        strokeDashArray: 5,
        padding: {
          left: -8,
          right: -15,
        },
      },
      fill: {
        opacity: 1
      },
      tooltip: {
        y: {
          formatter: function (val) {
            return "" + val + "%"
          }
        }
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#s-col"),
      sCol
    );

    chart.render();
  }

  if ($('#earnings-chart').length > 0) {
    var sCol = {
      chart: {
        height: 390,
        type: 'bar',
        toolbar: {
          show: false,
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '50%',
          borderRadius: 10,
          borderRadiusApplication: 'end', // this makes only the top of vertical bars rounded
          endingShape: 'rounded',
        },
      },
      colors: ['#7539FF'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: true,
        width: 2,
        colors: ['transparent']
      },

      series: [{
        name: 'Income',
        data: [28, 28, 43, 75, 45, 38, 47,28, 33, 23, 58, 40]
      }],
      xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        labels: {
          style: {
            colors: '#051321',
            fontSize: '14px',
          }
        }
      },
      yaxis: {
        max: 100,
        labels: {
          offsetX: -15,
          style: {
            colors: '#051321',
            fontSize: '14px',
          }
        }
      },
      grid: {
        borderColor: '#CED2D4',
        strokeDashArray: 5,
        padding: {
          left: -8,
          right: -15,
        },
      },
      fill: {
        opacity: 1
      },
      tooltip: {
        y: {
          formatter: function (val) {
            return "" + val + "%"
          }
        }
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#earnings-chart"),
      sCol
    );

    chart.render();
  }

  if ($('#register-chart').length > 0) {
    var sCol = {
      chart: {
        height: 320,
        type: 'area',
        toolbar: {
          show: false,
        },
        zoom: {
          enabled: false
        }
      },
      stroke: {
        curve: 'straight', // creates those spiky angles like in the image
        width: 1,
        colors: ['#7539FF']
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: '#7539FF',
          type: "vertical",
          shadeIntensity: 1,
          gradientToColors: ['#ffffff'], // fade into white
          inverseColors: false,
          opacityFrom: 0.9,
          opacityTo: 0,
          stops: [0, 100]
        }
      },
      colors: ['#7539FF'],
      dataLabels: {
        enabled: false
      },
      series: [{
        name: 'Companies Registered',
        data: [40, 30, 80, 25, 60, 25, 40,] // you can adjust this data
      }],
      xaxis: {
        categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        tickPlacement: 'between',
        labels: {
          style: {
            colors: '#051321',
            fontSize: '14px',
          }
        }
      },
      yaxis: {
        max: 100,
        labels: {
          offsetX: -15,
          style: {
            colors: '#051321',
            fontSize: '14px',
          }
        }
      },
      grid: {
        borderColor: '#CED2D4',
        strokeDashArray: 5,
        padding: {
          left: -8,
          right: -15,
        },
      },
      tooltip: {
        y: {
          formatter: function (val) {
            return val + " companies";
          }
        }
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#register-chart"),
      sCol
    );

    chart.render();
  }

  if ($('#plane-chart').length > 0) {
    var options = {
      series: [{
        data: [400, 325, 312, 294, 254, 254]
      }],
      chart: {
        type: 'bar',
        height: 300,
        fontFamily: 'Inter, sans-serif',
        toolbar: { show: false }
      },
      plotOptions: {
        bar: {
          barHeight: '100%',
          distributed: true,
          horizontal: true,
        }
      },
      dataLabels: {
        enabled: true,
        style: {
          fontSize: '14px',
          fontWeight: '500',
          colors: ['#1D1D1D']
        },
        formatter: function (val, opt) {
          // Show label from category with value
          return categories[opt.dataPointIndex] + ": " + val;
          show
        },
        offsetX: 10,
        dropShadow: {
          enabled: false
        }
      },
      grid: {
        padding: {
        left: -10,
        right: 0,
        top: 0,
        bottom: -15
        }
      },
      legend: {
        show: false
      },
      colors: ['#FFECEC', '#DDF3FF', '#EADDFF', '#E1FFED', '#EADFF0', '#FFF8E7'],
      stroke: {
        width: 0,
        colors: ['#1D1D1D'],
      },
      xaxis: {
        labels: {
          show: false
        },
        axisBorder: {
          show: false
        },
        axisTicks: {
          show: false
        }
      },
      yaxis: {
        labels: {
          show: false
        },
        axisBorder: {
          show: false
        },
        axisTicks: {
          show: false
        }
      },
      tooltip: {
        x: {
          show: false
        },
        y: {
          title: {
            formatter: function () {
              return ''; // Hide the title
            }
          },
          formatter: function (val, opts) {
            return categories[opts.dataPointIndex] + ': ' + val;
          }
        }
      }
    };

    // Categories used for labeling inside dataLabels
    const categories = [
      'Enterprise (Monthly) • Sales: $6,100.00',
      'Basic (Yearly) • Sales: $5,100.00',
      'Advanced (Monthly) • Sales: $4,200.00',
      'Enterprise (Yearly) • Sales: $4,100.00',
      'Basic (Monthly) • Sales: $3,100.00',
      'Advanced (Monthly) • Sales: $2,900.00'
    ];

    var chart = new ApexCharts(document.querySelector("#plane-chart"), options);
    chart.render();
  }


  // Simple Column Stacked
  if ($('#s-col-stacked').length > 0) {
    var sColStacked = {
      chart: {
        height: 290,
        type: 'bar',
        stacked: true,
        toolbar: {
          show: false,
        }
      },
      responsive: [{
        breakpoint: 480,
        options: {
          legend: {
            position: 'bottom',
            offsetX: -10,
            offsetY: 0
          }
        }
      }],
      plotOptions: {
        bar: {
          horizontal: false,
        },
      },
      colors: ['#3550DC', '#E70D0D', '#03C95A', '#1B84FF'],
      series: [{
        name: 'PRODUCT A',
        data: [44, 55, 41, 67, 22, 43]
      }, {
        name: 'PRODUCT B',
        data: [13, 23, 20, 8, 13, 27]
      }, {
        name: 'PRODUCT C',
        data: [11, 17, 15, 15, 21, 14]
      }, {
        name: 'PRODUCT D',
        data: [21, 7, 25, 13, 22, 8]
      }],
      xaxis: {
        type: 'datetime',
        categories: ['01/01/2011 GMT', '01/02/2011 GMT', '01/03/2011 GMT', '01/04/2011 GMT', '01/05/2011 GMT', '01/06/2011 GMT'],
      },
      legend: {
        position: 'right',
        offsetY: 40
      },
      fill: {
        opacity: 1
      },
    }

    var chart = new ApexCharts(
      document.querySelector("#s-col-stacked"),
      sColStacked
    );

    chart.render();
  }

  // Simple Bar
  if ($('#s-bar').length > 0) {
    var sBar = {
      chart: {
        height: 350,
        type: 'bar',
        toolbar: {
          show: false,
        }
      },
      colors: ['#3550DC'],
      plotOptions: {
        bar: {
          horizontal: true,
        }
      },
      dataLabels: {
        enabled: false
      },
      series: [{
        data: [400, 430, 448, 470, 540, 580, 690, 1100, 1200, 1380]
      }],
      xaxis: {
        categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy', 'France', 'Japan', 'United States', 'China', 'Germany'],
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#s-bar"),
      sBar
    );

    chart.render();
  }


  // Activities bar
  if ($('#a-bar').length > 0) {
  var sBar = {
    chart: {
      height: 400,
      type: 'bar',
      toolbar: {
        show: false,
      }
    },
    colors: ['#3550dc', '#ff8f28', '#ab47bc', '#0080ff', '#27eaea', '#ced2d4'],
    plotOptions: {
      bar: {
        horizontal: true,
        distributed: true,
        barHeight: '80%'
      }
    },
    dataLabels: {
      enabled: false
    },
    series: [{
      data: [30, 25, 10, 20, 15, 5] // Matches values from image
    }],
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      labels: {
        style: {
          fontSize: '14px'
        }
      }
    },
    grid: {
      xaxis: {
        lines: {
          show: false
        }
      }
    }
  }

  var chart = new ApexCharts(
    document.querySelector("#a-bar"),
    sBar
  );

  chart.render();
}

  // Mixed Chart
  if ($('#mixed-chart').length > 0) {
    var options = {
      chart: {
        height: 350,
        type: 'line',
        toolbar: {
          show: false,
        }
      },
      colors: ['#3550DC', '#888ea8'],
      series: [{
        name: 'Website Blog',
        type: 'column',
        data: [440, 505, 414, 671, 227, 413, 201, 352, 752, 320, 257, 160]
      }, {
        name: 'Social Media',
        type: 'line',
        data: [23, 42, 35, 27, 43, 22, 17, 31, 22, 22, 12, 16]
      }],
      stroke: {
        width: [0, 4]
      },
      title: {
        text: 'Traffic Sources'
      },
      labels: ['01 Jan 2001', '02 Jan 2001', '03 Jan 2001', '04 Jan 2001', '05 Jan 2001', '06 Jan 2001', '07 Jan 2001', '08 Jan 2001', '09 Jan 2001', '10 Jan 2001', '11 Jan 2001', '12 Jan 2001'],
      xaxis: {
        type: 'datetime'
      },
      yaxis: [{
        title: {
          text: 'Website Blog',
        },

      }, {
        opposite: true,
        title: {
          text: 'Social Media'
        }
      }]

    }

    var chart = new ApexCharts(
      document.querySelector("#mixed-chart"),
      options
    );

    chart.render();
  }

  // Donut Chart

  if ($('#donut-chart').length > 0) {
    var donutChart = {
      chart: {
        height: 350,
        type: 'donut',
        toolbar: {
          show: false,
        }
      },
      // colors: ['#4361ee', '#888ea8', '#e3e4eb', '#d3d3d3'],
      series: [44, 55, 41, 17],
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    }

    var donut = new ApexCharts(
      document.querySelector("#donut-chart"),
      donutChart
    );

    donut.render();
  }

  // Radial Chart
  if ($('#radial-chart').length > 0) {
    var radialChart = {
      chart: {
        height: 350,
        type: 'radialBar',
        toolbar: {
          show: false,
        }
      },
      // colors: ['#4361ee', '#888ea8', '#e3e4eb', '#d3d3d3'],
      plotOptions: {
        radialBar: {
          dataLabels: {
            name: {
              fontSize: '22px',
            },
            value: {
              fontSize: '16px',
            },
            total: {
              show: true,
              label: 'Total',
              formatter: function (w) {
                return 249
              }
            }
          }
        }
      },
      series: [44, 55, 67, 83],
      labels: ['Apples', 'Oranges', 'Bananas', 'Berries'],
    }

    var chart = new ApexCharts(
      document.querySelector("#radial-chart"),
      radialChart
    );

    chart.render();
  }

   // Radial Chart2
   if ($('#radial-chart2').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 164,
      },
      series: [30, 10, 30, 30],
      labels: ['Total', 'Total', 'Total', 'Total'],
      colors: ['#7539FF', '#E2B93B', '#27AE60', '#DD2590'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false, // No gap between segments
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '70%',
            labels: {
              show: true, // ✅ Ensure donut center is always visible
              name: {
                show: true,
                text: 'Total',
                fontSize: '13px',
                offsetY: -4,
                color: '#5D6772'
              },
              value: {
                show: true,
                fontSize: '18px',
                fontWeight: 700,
                offsetY: 10,
                color: '#051321',
                formatter: function () {
                  return "$3656"; // ✅ Always shows this value
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart2"),
      options
    );

    chart.render();
  }

   // Radial Chart3
   if ($('#radial-chart3').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#7539FF', '#EFEEFF'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '80%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart3"),
      options
    );

    chart.render();
  }

     // Radial Chart4
     if ($('#radial-chart4').length > 0) {
      var options = {
        chart: {
          type: 'donut',
          height: 49,
          width: 49,
        },
        series: [75, 25], // Adjust this for progress percentage
        labels: ['Completed', 'Remaining'],
        colors: ['#27AE60', '#E9F7EF'],
        legend: {
          show: false
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: false
        },
        plotOptions: {
          pie: {
            expandOnClick: false,
            donut: {
              size: '80%', // Adjust for better inner circle spacing
              labels: {
                show: true,
                name: {
                  show: false
                },
                value: {
                  show: true,
                  fontSize: '10px', // Small font to fit the size
                  fontWeight: 600,
                  offsetY: 0,
                  color: '#7539FF',
                  formatter: function () {
                    return '75%'; // or any other center label
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: false
        }
      };

      var chart = new ApexCharts(
        document.querySelector("#radial-chart4"),
        options
      );

      chart.render();
    }


    // Radial Chart5
    if ($('#radial-chart5').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#E2B93B', '#FCF8EB'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '80%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart5"),
      options
    );

    chart.render();
  }

  // Radial Chart6
    if ($('#radial-chart6').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#EF1E1E', '#FDE9E9'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '80%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart6"),
      options
    );

    chart.render();
  }

  // Radial Chart7
  if ($('#radial-chart7').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#27AE60', '#EFEEFF'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '60%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart7"),
      options
    );

    chart.render();
  }

  // Radial Chart8
  if ($('#radial-chart8').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#E2B93B', '#EFEEFF'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '60%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart8"),
      options
    );

    chart.render();
  }

  // Radial Chart9
  if ($('#radial-chart9').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#EF1E1E', '#EFEEFF'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '60%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart9"),
      options
    );

    chart.render();
  }

  // Radial Chart10
  if ($('#radial-chart10').length > 0) {
    var options = {
      chart: {
        type: 'donut',
        height: 49,
        width: 49,
      },
      series: [75, 25], // Adjust this for progress percentage
      labels: ['Completed', 'Remaining'],
      colors: ['#7539FF', '#EFEEFF'],
      legend: {
        show: false
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: false
      },
      plotOptions: {
        pie: {
          expandOnClick: false,
          donut: {
            size: '60%', // Adjust for better inner circle spacing
            labels: {
              show: true,
              name: {
                show: false
              },
              value: {
                show: true,
                fontSize: '10px', // Small font to fit the size
                fontWeight: 600,
                offsetY: 0,
                color: '#7539FF',
                formatter: function () {
                  return '75%'; // or any other center label
                }
              }
            }
          }
        }
      },
      tooltip: {
        enabled: false
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#radial-chart10"),
      options
    );

    chart.render();
  }

    // Radial Chart11
    if ($('#radial-chart11').length > 0) {
      var options = {
        chart: {
          type: 'donut',
          height: 49,
          width: 49,
        },
        series: [75, 25], // Adjust this for progress percentage
        labels: ['Completed', 'Remaining'],
        colors: ['#7539FF', '#EFEEFF'],
        legend: {
          show: false
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: false
        },
        plotOptions: {
          pie: {
            expandOnClick: false,
            donut: {
              size: '60%', // Adjust for better inner circle spacing
              labels: {
                show: true,
                name: {
                  show: false
                },
                value: {
                  show: true,
                  fontSize: '10px', // Small font to fit the size
                  fontWeight: 600,
                  offsetY: 0,
                  color: '#7539FF',
                  formatter: function () {
                    return '75%'; // or any other center label
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: false
        }
      };

      var chart = new ApexCharts(
        document.querySelector("#radial-chart11"),
        options
      );

      chart.render();
    }

    // Radial Chart12
    if ($('#radial-chart12').length > 0) {
      var options = {
        chart: {
          type: 'donut',
          height: 49,
          width: 49,
        },
        series: [75, 25], // Adjust this for progress percentage
        labels: ['Completed', 'Remaining'],
        colors: ['#27AE60', '#EFEEFF'],
        legend: {
          show: false
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: false
        },
        plotOptions: {
          pie: {
            expandOnClick: false,
            donut: {
              size: '60%', // Adjust for better inner circle spacing
              labels: {
                show: true,
                name: {
                  show: false
                },
                value: {
                  show: true,
                  fontSize: '10px', // Small font to fit the size
                  fontWeight: 600,
                  offsetY: 0,
                  color: '#7539FF',
                  formatter: function () {
                    return '75%'; // or any other center label
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: false
        }
      };

      var chart = new ApexCharts(
        document.querySelector("#radial-chart12"),
        options
      );

      chart.render();
    }

    // Radial Chart13
    if ($('#radial-chart13').length > 0) {
      var options = {
        chart: {
          type: 'donut',
          height: 49,
          width: 49,
        },
        series: [75, 25], // Adjust this for progress percentage
        labels: ['Completed', 'Remaining'],
        colors: ['#E2B93B', '#EFEEFF'],
        legend: {
          show: false
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: false
        },
        plotOptions: {
          pie: {
            expandOnClick: false,
            donut: {
              size: '60%', // Adjust for better inner circle spacing
              labels: {
                show: true,
                name: {
                  show: false
                },
                value: {
                  show: true,
                  fontSize: '10px', // Small font to fit the size
                  fontWeight: 600,
                  offsetY: 0,
                  color: '#7539FF',
                  formatter: function () {
                    return '75%'; // or any other center label
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: false
        }
      };

      var chart = new ApexCharts(
        document.querySelector("#radial-chart13"),
        options
      );

      chart.render();
    }

    // Radial Chart14
    if ($('#radial-chart14').length > 0) {
      var options = {
        chart: {
          type: 'donut',
          height: 49,
          width: 49,
        },
        series: [75, 25], // Adjust this for progress percentage
        labels: ['Completed', 'Remaining'],
        colors: ['#EF1E1E', '#EFEEFF'],
        legend: {
          show: false
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: false
        },
        plotOptions: {
          pie: {
            expandOnClick: false,
            donut: {
              size: '60%', // Adjust for better inner circle spacing
              labels: {
                show: true,
                name: {
                  show: false
                },
                value: {
                  show: true,
                  fontSize: '10px', // Small font to fit the size
                  fontWeight: 600,
                  offsetY: 0,
                  color: '#7539FF',
                  formatter: function () {
                    return '75%'; // or any other center label
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: false
        }
      };

      var chart = new ApexCharts(
        document.querySelector("#radial-chart14"),
        options
      );

      chart.render();
    }


  // end chart

  if ($('#sales_charts').length > 0) {
    var options = {
      series: [{
        name: 'Sales',
        data: [130, 210, 300, 290, 150, 50, 210, 280, 105],
      }, {
        name: 'Purchase',
        data: [-150, -90, -50, -180, -50, -70, -100, -90, -105]
      }],
      colors: ['#28C76F', '#EA5455'],
      chart: {
        type: 'bar',
        height: 320,
        stacked: true,

        zoom: {
          enabled: true
        }
      },
      responsive: [{
        breakpoint: 280,
        options: {
          legend: {
            position: 'bottom',
            offsetY: 0
          }
        }
      }],
      plotOptions: {
        bar: {
          horizontal: false,
          borderRadius: 4,
          borderRadiusApplication: "end", // "around" / "end"
          borderRadiusWhenStacked: "all", // "all"/"last"
          columnWidth: '20%',
        },
      },
      dataLabels: {
        enabled: false
      },
      yaxis: {
        min: -200,
        max: 300,
        tickAmount: 5,
      },
      xaxis: {
        categories: [' Jan ', 'Feb', 'Mar', 'Apr',
          'May', 'Jun', 'Jul', 'Aug', 'Sep'
        ],
      },
      legend: { show: false },
      fill: {
        opacity: 1
      }
    };

    var chart = new ApexCharts(document.querySelector("#sales_charts"), options);
    chart.render();
  }

  if ($('#sales-analysis').length > 0) {
    var options = {
      series: [{
        name: "Sales Analysis",
        data: [25, 30, 18, 15, 22, 20, 30, 20, 22, 18, 15, 20]
      }],
      chart: {
        height: 273,
        type: 'area',
        zoom: {
          enabled: false
        }
      },
      colors: ['#FF9F43'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'straight'
      },
      title: {
        text: '',
        align: 'left'
      },
      xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
      },
      yaxis: {
        min: 10,
        max: 60,
        tickAmount: 5,
        labels: {
          formatter: (val) => {
            return val / 1 + 'K'
          }
        }
      },
      legend: {
        position: 'top',
        horizontalAlign: 'left'
      }
    };

    var chart = new ApexCharts(document.querySelector("#sales-analysis"), options);
    chart.render();
  }

  // Student Chart

  if ($('#teacher-chart').length > 0) {
    var donutChart = {
      chart: {
        height: 260,
        type: 'donut',
        toolbar: {
          show: false,
        }
      },
      colors: ['#3D5EE1', '#6FCCD8'],
      series: [346, 54],
      labels: ['Present', 'Absent'],
      legend: { show: false },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            height: 180,
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    }

    var donut = new ApexCharts(
      document.querySelector("#teacher-chart"),
      donutChart
    );

    donut.render();
  }


  // Student Chart

  if ($('#staff-chart').length > 0) {
    var donutChart = {
      chart: {
        height: 260,
        type: 'donut',
        toolbar: {
          show: false,
        }
      },
      colors: ['#3D5EE1', '#6FCCD8'],
      series: [620, 80],
      labels: ['Present', 'Absent'],
      legend: { show: false },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            height: 180,
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    }

    var donut = new ApexCharts(
      document.querySelector("#staff-chart"),
      donutChart
    );

    donut.render();
  }


  // Class Chart

  if ($('#class-chart').length > 0) {
    var donutChart = {
      chart: {
        height: 130,
        type: 'donut',
        toolbar: {
          show: false,
        },
        sparkline: {
          enabled: true
        }
      },
      colors: ['#3D5EE1', '#EAB300', '#E82646'],
      series: [45, 11, 2],
      labels: ['Good', 'Average', 'Below Average'],
      legend: { show: false },
      dataLabels: {
        enabled: false
      },
      yaxis: {
        tickAmount: 3,
        labels: {
          offsetX: -15,
        },
      },
      grid: {
        padding: {
          left: -8,
        },
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    }

    var donut = new ApexCharts(
      document.querySelector("#class-chart"),
      donutChart
    );

    donut.render();
  }

  // Leaves Chart

  if ($('#web_chart').length > 0) {
    var donutChart = {
      chart: {
        height: 205,
        type: 'donut',
        toolbar: {
          show: false,
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '30%',
        },
      },
      dataLabels: {
        enabled: false
      },
      series: [41, 11, 7, 18, 6, 12, 4, 16],
      colors: ['#FF7F00', '#FF0000', '#8000FF', '#27EAEA', '#01B664', '#F9B801', '#24CDBA', '#AB47BC'],
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 50,
          },
          legend: {
            show: false
          }
        }
      }],
      legend: {
        show: false
      }
    }

    var donut = new ApexCharts(
      document.querySelector("#web_chart"),
      donutChart
    );

    donut.render();
  }

  // Fees Chart

  if ($('#fees-chart').length > 0) {
    var sCol = {
      chart: {
        height: 275,
        type: 'bar',
        stacked: true,
        toolbar: {
          show: false,
        }
      },
      legend: {
        show: true,
        horizontalAlign: 'left',
        position: 'top',
        fontSize: '14px',
        labels: {
          colors: '#5D6369',
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '50%',
          endingShape: 'rounded'
        },
      },
      colors: ['#3D5EE1', '#E9EDF4'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: true,
        width: 2,
        colors: ['transparent']
      },
      grid: {
        padding: {
          left: -8,
        },
      },
      series: [{
        name: 'Collected Fee',
        data: [30, 40, 38, 40, 38, 30, 35, 38, 40]
      }, {
        name: 'Total Fee',
        data: [45, 50, 48, 50, 48, 40, 40, 50, 55]
      }],
      xaxis: {
        categories: ['Q1: 2023', 'Q1: 2023', 'Q1: 2023', 'Q1: 2023', 'Q1: 2023', 'uQ1: 2023l', 'Q1: 2023', 'Q1: 2023', 'Q1: 2023'],
      },
      yaxis: {
      },
      yaxis: {
        tickAmount: 3,
        labels: {
          offsetX: -15
        },
      },
      fill: {
        opacity: 1

      },
      tooltip: {
        y: {
          formatter: function (val) {
            return "$ " + val + " thousands"
          }
        }
      }
    }

    var chart = new ApexCharts(
      document.querySelector("#fees-chart"),
      sCol
    );

    chart.render();
  }

  if ($('#exam-result-chart').length > 0) {
    var options = {
      chart: {
        type: 'bar',
        height: 310
      },
      series: [{
        name: 'Marks',
        data: [100, 92, 90, 82, 90] // Corresponding scores for Maths, Physics, Chemistry, English, Spanish
      }],
      xaxis: {
        categories: ['Mat', 'Phy', 'Che', 'Eng', 'Sci']
      },
      plotOptions: {
        bar: {
          distributed: true,
          columnWidth: '50%',
          colors: {
            backgroundBarColors: ['#E9EDF4', '#fff'],
            backgroundBarOpacity: 1,
            backgroundBarRadius: 5,
          },
          dataLabels: {
            position: 'top'
          },
        }
      },
      colors: ['#E9EDF4', '#3D5EE1', '#E9EDF4', '#E9EDF4', '#E9EDF4'], // Set specific colors for each bar
      tooltip: {
        y: {
          formatter: function (val) {
            return val + "%"
          }
        }
      },
      dataLabels: {
        enabled: true,
        formatter: function (val) {
          return val + "%";
        },
        offsetY: -20,
        style: {
          fontSize: '14px',
          colors: ["#304758"]
        }
      },
      grid: {
        yaxis: {
          lines: {
            show: false
          }
        },
      },

      legend: {
        show: false
      }
    }

    var chart = new ApexCharts(document.querySelector("#exam-result-chart"), options);
    chart.render();
  }

  if ($('#performance_chart').length > 0) {
    var options = {
      chart: {
        type: 'area',
        height: 355
      },
      series: [{
        name: 'Avg. Exam Score',
        data: [75, 68, 65, 68, 75] // Sample data
      }, {
        name: 'Avg. Attendance',
        data: [85, 78, 75, 78, 85] // Sample data
      }],
      xaxis: {
        categories: ['Quarter 1', 'Quarter 2', 'Half yearly', 'Model', 'Final']
      },
      tooltip: {
        y: {
          formatter: function (val) {
            return val + "%";
          }
        },
        shared: true,
        intersect: false,
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          return `<div class="apexcharts-tooltip">${w.globals.labels[dataPointIndex]}<br>Exam Score: <span style="color: #1E90FF;">${series[0][dataPointIndex]}%</span><br>Attendance: <span style="color: #00BFFF;">${series[1][dataPointIndex]}%</span></div>`;
        }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth'
      },
      grid: {
        padding: {
          left: -15,
          right: 0,
        },
      },
      grid: {
        yaxis: {
          axisTicks: {
            show: true,
            borderType: 'solid',
            color: '#78909C',
            width: 6,
            offsetX: 0,
            offsetY: 0
          },

        },
      },
      yaxis: {
        labels: {
          offsetX: -15
        },
      },
      markers: {
        size: 5,
        colors: ['#1E90FF', '#00BFFF'],
        strokeColors: '#fff',
        strokeWidth: 2,
        hover: {
          size: 7
        }
      },
      colors: ['#3D5EE1', '#6FCCD8'], // Color for the lines
      fill: {
        type: 'gradient',
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.7,
          opacityTo: 0.9,
          stops: [0, 90, 100]
        }
      },
      legend: {
        position: 'bottom',
        horizontalAlign: 'center'
      }
    }
    var chart = new ApexCharts(document.querySelector("#performance_chart"), options);
    chart.render();
  }

  // Plan Chart

  if ($('#plan_chart').length > 0) {
    var donutChart = {
      chart: {
        height: 90,
        type: 'donut',
        toolbar: {
          show: false,
        },
        sparkline: {
          enabled: true
        }
      },
      grid: {
        show: false,
        padding: {
          left: 0,
          right: 0
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '50%'
        },
      },
      dataLabels: {
        enabled: false
      },

      series: [95, 5],
      labels: [
        'Completed',
        'Pending'

      ],
      legend: { show: false },
      colors: ['#3D5EE1', '#E82646'],
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 100
          },
          legend: {
            position: 'bottom'
          }
        }
      }],
      legend: {
        position: 'bottom'
      }
    }

    var donut = new ApexCharts(
      document.querySelector("#plan_chart"),
      donutChart
    );

    donut.render();
  }

  if ($('#statistic_chart').length > 0) {
    var options = {
      chart: {
        type: 'line',
        height: 345,
      },
      series: [{
        name: 'Avg. Exam Score',
        data: [0, 32, 40, 50, 60, 52, 50, 44, 40, 60, 75, 70] // Sample data
      }, {
        name: 'Avg. Attendance',
        data: [0, 35, 43, 34, 30, 28, 25, 50, 60, 75, 77, 80] // Sample data
      }],
      xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      },
      tooltip: {
        y: {
          formatter: function (val) {
            return val + "%";
          }
        },
        shared: true,
        intersect: false,
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          return `<div class="apexcharts-tooltip">${w.globals.labels[dataPointIndex]}<br>Exam Score: <span style="color: #1E90FF;">${series[0][dataPointIndex]}%</span><br>Attendance: <span style="color: #00BFFF;">${series[1][dataPointIndex]}%</span></div>`;
        }
      },
      dataLabels: {
        enabled: false
      },
      grid: {
        yaxis: {
          lines: {
            show: true
          }
        },
      },
      yaxis: {
        labels: {
          offsetX: -15
        },
      },
      grid: {
        padding: {
          left: -8,
        },
      },
      markers: {
        size: 0,
        colors: ['#1E90FF', '#00BFFF'],
        strokeColors: '#fff',
        strokeWidth: 1,
        hover: {
          size: 7
        }
      },
      colors: ['#3D5EE1', '#6FCCD8'], // Color for the lines
      legend: {
        position: 'top',
        horizontalAlign: 'left'
      }
    }
    var chart = new ApexCharts(document.querySelector("#statistic_chart"), options);
    chart.render();
  }

  if ($('#attendance_chart2').length > 0) {
    var donutChart = {
      chart: {
        height: 290,
        type: 'donut',
        toolbar: {
          show: false,
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '50%'
        },
      },
      dataLabels: {
        enabled: false
      },

      series: [60, 5, 15, 20],
      labels: [
        'Present',
        'Late',
        'Half Day',
        'Absent'
      ],
      colors: ['#1ABE17', '#1170E4', '#E9EDF4', '#E82646'],
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200
          },
          legend: {
            position: 'left'
          }
        }
      }],
      legend: {
        position: 'left',
      }
    }

    var donut = new ApexCharts(
      document.querySelector("#attendance_chart2"),
      donutChart
    );

    donut.render();
  }

  // Total Earning
  if ($('#total-earning').length > 0) {
    var sLineArea = {
      chart: {
        height: 90,
        type: 'area',
        toolbar: {
          show: false,
        },
        sparkline: {
          enabled: true
        }
      },
      colors: ['#3D5EE1'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'straight'
      },
      series: [{
        name: 'Earnings',
        data: [50, 60, 40, 50, 45, 55, 50]
      }]
    }

    var chart = new ApexCharts(
      document.querySelector("#total-earning"),
      sLineArea
    );

    chart.render();
  }

  // Total Expenses
  if ($('#total-expenses').length > 0) {
    var sLineArea = {
      chart: {
        height: 90,
        type: 'area',
        toolbar: {
          show: false,
        },
        sparkline: {
          enabled: true
        }
      },
      colors: ['#E82646'],
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'straight'
      },
      series: [{
        name: 'Earnings',
        data: [40, 20, 60, 55, 50, 55, 40]
      }]
    }

    var chart = new ApexCharts(
      document.querySelector("#total-expenses"),
      sLineArea
    );

    chart.render();
  }

  // Statistic Chart
  if ($('#statistic-chart').length > 0) {
    const options = {
      series: [{
        labels: ['Orders'],
        data: [40, 35, 45, 44, 63,  50, 84]
      }],
      chart: {
        height: 260,
        type: 'area',
        zoom: {
          enabled: false
        },
        toolbar: {
          show: false
        }
      },
      tooltip: {
        enabled: true,
        x: {
          show: true
        },
        y: {
          title: {
            formatter: function (seriesName) {
              return ''
            }
          }
        },
        marker: {
          show: false
        }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth',
        width: [1.5],
      },
      fill: {
        type: "gradient",     // or 'gradient'
        opacity: 0.2,      // reduce area darkness (0 = no fill, 1 = solid)
        
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.4,
          opacityTo: 0.9,
          stops: [0, 90, 100],
          colorStops: [
            {
              offset: 0,
              color: "#4da5ff",
              opacity: 0.8
            },
            {
              offset: 100,
              color: "#ffffff",
              opacity: 0
            }
          ]
        }
      },
      title: {
        text: undefined,
      },
      grid: {
        borderColor: 'transparent',
        strokeDashArray: 0,
        xaxis: { lines: { show: false } },
        yaxis: { lines: { show: false } },
        padding: {
            left: 2,
            right: -3,
            top: -50
          }
      },
      xaxis: {
        categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        labels: {
          style: {
            fontSize: '12px',
          }
        }
      },
      yaxis: {
      min: 0,
      forceNiceScale: true,
      labels: {
        show: false
      }
    },
      colors: ["#4da5ff"],
    };
    const chart = new ApexCharts(document.querySelector("#statistic-chart"), options);
    chart.render();
  }

});

// Donut Chart

if ($('#storage-chart').length > 0) {
  var donutChart = {
    chart: {
      height: 200,
      type: 'donut',
      toolbar: {
        show: false,
      },
      offsetY: -10,
      events: {
        rendered: function () {
          // Adding the center text
          var chartElement = document.querySelector("#donutChart");
          var innerText = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">' +
            '<span style="font-size: 24px; font-weight: bold;">Total</span><br>' +
            '<span style="font-size: 16px;">abb</span>' +
            '</div>';
          chartElement.innerHTML += innerText;
        }
      },
    },
    plotOptions: {
      pie: {
        startAngle: -100,
        endAngle: 100,
        donut: {
          size: '80%',
          labels: {
            show: true,
            name: {
              show: true,
            }
          }
        }
      }
    },
    dataLabels: {
      enabled: false
    },
    legend: {
      show: false
    },
    stroke: {
      show: false
    },
    colors: ['#0C4B5E', '#FFC107', '#1B84FF', '#AB47BC', '#FD3995'],
    series: [20, 20, 20, 20, 20],
    labels: ['Documents', 'Video', 'Music', 'Photos', 'Other'],
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 200
        },
        legend: {
          position: 'bottom'
        }
      }
    }],
    grid: {
      padding: {
        bottom: -60  // Reduce padding from the bottom
      }
    }
  }

  var donut = new ApexCharts(
    document.querySelector("#storage-chart"),
    donutChart
  );

  donut.render();
}



// s-col-1
if ($('#s-col-1').length > 0) {
  var sCol = {
    chart: {
      width: 40,
      height: 54,
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '70%',
        borderRadius: 0,
        endingShape: 'rounded'
      }
    },
    dataLabels: { enabled: false },
    stroke: { show: false },
    series: [{
      name: 'Data',
      data: [
        { x: 'A', y: 80, fillColor: '#3550DC' },
        { x: 'B', y: 35, fillColor: '#3550DC' },
        { x: 'C', y: 50, fillColor: '#3550DC' },
        { x: 'D', y: 45, fillColor: '#3550DC' },
        { x: 'E', y: 35, fillColor: '#3550DC' }
      ]
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#s-col-1"), sCol);
  chart.render();
}

// s-col-2
if ($('#s-col-2').length > 0) {
  var sCol = {
    chart: {
      width: 40,
      height: 54,
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '70%',
        borderRadius: 0,
        endingShape: 'rounded'
      }
    },
    dataLabels: { enabled: false },
    stroke: { show: false },
    series: [{
      name: 'Data',
      data: [
        { x: 'A', y: 90, fillColor: '#01B664' },
        { x: 'B', y: 35, fillColor: '#01B664' },
        { x: 'C', y: 40, fillColor: '#01B664' },
        { x: 'D', y: 65, fillColor: '#01B664' },
        { x: 'E', y: 55, fillColor: '#01B664' }
      ]
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#s-col-2"), sCol);
  chart.render();
}

// s-col-3
if ($('#s-col-3').length > 0) {
  var sCol = {
    chart: {
      width: 40,
      height: 54,
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '70%',
        borderRadius: 0,
        endingShape: 'rounded'
      }
    },
    dataLabels: { enabled: false },
    stroke: { show: false },
    series: [{
      name: 'Data',
      data: [
        { x: 'A', y: 90, fillColor: '#FF0000' },
        { x: 'B', y: 65, fillColor: '#FF0000' },
        { x: 'C', y: 60, fillColor: '#FF0000' },
        { x: 'D', y: 45, fillColor: '#FF0000' },
        { x: 'E', y: 25, fillColor: '#FF0000' }
      ]
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#s-col-3"), sCol);
  chart.render();
}

// s-col-4
if ($('#s-col-4').length > 0) {
  var sCol = {
    chart: {
      width: 40,
      height: 54,
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '70%',
        borderRadius: 0,
        endingShape: 'rounded'
      }
    },
    dataLabels: { enabled: false },
    stroke: { show: false },
    series: [{
      name: 'Data',
      data: [
        { x: 'A', y: 80, fillColor: '#FF0000' },
        { x: 'B', y: 85, fillColor: '#FF0000' },
        { x: 'C', y: 50, fillColor: '#FF0000' },
        { x: 'D', y: 55, fillColor: '#FF0000' },
        { x: 'E', y: 95, fillColor: '#FF0000' }
      ]
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#s-col-4"), sCol);
  chart.render();
}


// s-col-1
if ($('#chart-col-1').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#3550DC']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#3550dc",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-1"), sCol);
  chart.render();
}

// s-col-2
if ($('#chart-col-2').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#FE9738']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#f9b801",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-2"), sCol);
  chart.render();
}

// s-col-3
if ($('#chart-col-3').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#3550dc']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#3550dc",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-3"), sCol);
  chart.render();
}

// s-col-4
if ($('#chart-col-4').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#01B664']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#3e9ab5",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 45, 30, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-4"), sCol);
  chart.render();
}

// s-col-1
if ($('#chart-col-11').length > 0) {
  var sCol = {
    chart: {
      width: 100,
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#8000FF']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#8A3FFF40",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-11"), sCol);
  chart.render();
}

// s-col-2
if ($('#chart-col-12').length > 0) {
  var sCol = {
    chart: {
      width: 100,
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#FE9738']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#FE973840",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-12"), sCol);
  chart.render();
}

// s-col-3
if ($('#chart-col-13').length > 0) {
  var sCol = {
    chart: {
      width: 100,
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#3550dc']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#3550dc",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-13"), sCol);
  chart.render();
}

// s-col-4
if ($('#chart-col-14').length > 0) {
  var sCol = {
    chart: {
      width: 100,
      height: 54,
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: true }
    },
    stroke: {
      curve: 'smooth',
      width: 1,
      colors: ['#E22871']  // orange line
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0,
        stops: [0, 90, 100],
        colorStops: [
          {
            offset: 0,
            color: "#FF45FF40",
            opacity: 0.4
          },
          {
            offset: 100,
            color: "#ffffff",
            opacity: 0.8
          }
        ]
      }
    },
    dataLabels: { enabled: false },
    series: [{
      name: 'Data',
      data: [22, 35, 30, 40, 45, 30, 28, 45, 40] // You can adjust these
    }],
    xaxis: {
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false },
    grid: { show: false },
    tooltip: { enabled: false }
  };

  var chart = new ApexCharts(document.querySelector("#chart-col-14"), sCol);
  chart.render();
}

// Poductive Chart

if ($('#productivetime-chart').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 60,
      type: 'bar',
      toolbar: {
        show: false,
      },
      padding: 0
    },
    legend: {
      show: false
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '100%', // Removes space between bars
          barHeight: '100%',
        endingShape: 'rounded',
        distributed: true,
      },
    },
    colors: ['#FFF5ED', '#FFAD6A', '#FFF5ED', '#FFAD6A'],
    states: {
      hover: {
          filter: {
              type: 'darken', // Options: 'none', 'lighten', 'darken'
              value: 0.3 // Adjust hover intensity
          }
      }
  },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    series: [{
      name: 'Productive Time',
      data: [4, 8, 10, 14, 15, 16]
    }],
    fill: {
      opacity: 1

    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
  },
  grid: {
    show: false, // Set false to hide all grid lines
    padding: { left: 0, right: 0, top: -15, bottom: -28 }
},
    yaxis: {
      min: 4,
      max: 16,
      labels: { show: false }  // Hides Y-axis values
  },
    tooltip: {
      y: {
        formatter: function (val) {
          return  val
        }
      }
    }
  }

  var chart = new ApexCharts(
    document.querySelector("#productivetime-chart"),
    sCol
  );

  chart.render();
}

// Time Chart

if ($('#unproductivetime-chart').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 60,
      type: 'bar',
      toolbar: {
        show: false,
      },
      padding: 0
    },
    legend: {
      show: false
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '100%', // Removes space between bars
          barHeight: '100%',
        endingShape: 'rounded',
        distributed: true,
      },
    },
    colors: ['#35839a', '#F0ECFF', '#35839a','#F0ECFF',],
    states: {
      hover: {
          filter: {
              type: 'darken', // Options: 'none', 'lighten', 'darken'
              value: 0.3 // Adjust hover intensity
          }
      }
  },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    series: [{
      name: 'Unproductive Time',
      data: [5, 6, 7, 8, 9, 10]
    }],
    fill: {
      opacity: 1

    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
  },
  grid: {
    show: false, // Set false to hide all grid lines
    padding: { left: 0, right: 0, top: -15, bottom: -28 }
  },
    yaxis: {
      min: 3,
      max: 10,
      labels: { show: false }  // Hides Y-axis values
  },
    tooltip: {
      y: {
        formatter: function (val) {
          return  val
        }
      }
    }
  }

  var chart = new ApexCharts(
    document.querySelector("#unproductivetime-chart"),
    sCol
  );

  chart.render();
}

// Time Chart

if ($('#manualtime-chart').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 60,
      type: 'bar',
      toolbar: {
        show: false,
      },
      padding: 0
    },
    legend: {
      show: false
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '100%', // Removes space between bars
          barHeight: '100%',
        endingShape: 'rounded',
        distributed: true,
      },
    },
    colors: ['#EBF4F2', '#56A89B', '#EBF4F2', '#56A89B',],
    states: {
      hover: {
          filter: {
              type: 'darken', // Options: 'none', 'lighten', 'darken'
              value: 0.3 // Adjust hover intensity
          }
      }
  },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    series: [{
      name: 'Manual Time',
      data: [5, 7, 8, 10, 12, 14]
    }],
    fill: {
      opacity: 1

    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
  },
  grid: {
    show: false, // Set false to hide all grid lines
    padding: { left: 0, right: 0, top: -15, bottom: -28 }
},
    yaxis: {
      min: 3,
      max: 14,
      labels: { show: false }  // Hides Y-axis values
  },
    tooltip: {
      y: {
        formatter: function (val) {
          return  val
        }
      }
    }
  }

  var chart = new ApexCharts(
    document.querySelector("#manualtime-chart"),
    sCol
  );

  chart.render();
}

// Time Chart

if ($('#worktime-chart').length > 0) {
  var sCol = {
    chart: {
      width: '100%',
      height: 60,
      type: 'bar',
      toolbar: {
        show: false,
      },
      padding: 0
    },
    legend: {
      show: false
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '100%', // Removes space between bars
          barHeight: '100%',
        endingShape: 'rounded',
        distributed: true,
      },
    },
    colors: ['#E8EEFE', '#4361ee', '#E8EEFE', '#4361ee'],
    states: {
      hover: {
          filter: {
              type: 'darken', // Options: 'none', 'lighten', 'darken'
              value: 0.3 // Adjust hover intensity
          }
      }
  },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    series: [{
      name: 'Working Hours',
      data: [4,5, 6, 7, 10, 12]
    }],
    fill: {
      opacity: 1

    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false }
  },
  grid: {
    show: false, // Set false to hide all grid lines
    padding: { left: 0, right: 0, top: -15, bottom: -28 }
  },
    yaxis: {
      min: 2,
      max: 12,
      labels: { show: false }  // Hides Y-axis values
  },
    tooltip: {
      y: {
        formatter: function (val) {
          return  val
        }
      }
    }
  }

  var chart = new ApexCharts(
    document.querySelector("#worktime-chart"),
    sCol
  );

  chart.render();
}

if ($('#timeline_chart').length > 0) {
  var options = {
    series: [25, 15, 60], // Percentages for each section
    chart: {
        type: 'pie',
        height: 245,
    },
    labels: [ 'Unproductive', 'Overtime', 'Productive'], // Labels for the data
    colors: ['#8000FF', '#FE9738', '#24CDBA'], // Colors from the image
    plotOptions: {
        pie: {
          startAngle: 55,
            donut: {
                size: '60%',
                labels: {
                    show: false,
                    total: {
                        show: true,
                        label: 'Leads',
                        formatter: function (w) {
                            return '589';
                        }
                    }
                }
            }
        }
    },
    dataLabels: {
      enabled: true
    },
    legend: {
      show: false,
    },
    label: {
      show: false,
    }
};

var chart = new ApexCharts(document.querySelector("#timeline_chart"), options);
chart.render();
}


if ($('#project-chart').length > 0) {
  const sCol = {
    chart: {
      height: 294,
      type: 'bar',
      toolbar: {
        show: false,
      }
    },
    legend: {
      show: false
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '75%',
        borderRadius: 0,
        endingShape: 'square', // This rounds the top edges of the bars
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },

    series: [{
      name: 'Active',
      data: [89, 45, 89, 46, 61, 25, 79]
    }, {
      name: 'Inprogress',
      data: [19, 70, 19, 19, 19, 19, 19]
    },
    {
      name: 'Completed',
      data: [39, 39, 39, 80, 48, 48, 48]
    }],
    xaxis: {
      categories: ['15 Jan', '16 Jan', '17 Jan', '18 Jan', '19 Jan', '20 Jan', '21 Jan'],
      labels: {
        style: {
          colors: '#0C1C29',
          fontSize: '12px',
        }
      }
    },
    yaxis: {
      labels: {
        offsetX: -15,
        style: {
          colors: '#6D777F',
          fontSize: '14px',
        }
      }
    },
    grid: {
      borderColor: '#CED2D4',
      strokeDashArray: 5,
      padding: {
        left: -8,
        right: -15,
      },
    },
    fill: {
      opacity: 1
    },
    tooltip: {
      y: {
        formatter: function (val) {
          return "" + val + "%"
        }
      }
    },
    responsive: [{
          breakpoint: 991,
          options: {
            chart: {
              height: 290,
            }
          }
        }],


    colors: ["var(--primary)", "var(--secondary)", "var(--success)" ],
  }

  const chart = new ApexCharts(
    document.querySelector("#project-chart"),
    sCol
  );

  chart.render();
}

// Production Chart
if ($('#production_chart').length > 0) {
  var radialChart = {
    chart: {
      //height: '130px',
      //width: '100%',
      height: 120,
      type: 'radialBar',
      parentHeightOffset: 0,
      offsetX: 0,
      offsetY: 0,
      toolbar: { show: false }
    },
    plotOptions: {
      radialBar: {
        hollow: {
          margin: 10,
          size: '30%',
        },
        track: {
          background: '#F3F4F6',
          strokeWidth: '100%',
          margin: 5,
        },
        dataLabels: {
          name: {
            offsetY: -5,
          },
          value: {
            offsetY: 5,
          },
        },
      },
    },
    grid: {
      padding: {
        top: -20,
        bottom: -20,
        left: -40,
        right: -10,
      },
    },
    stroke: {
      lineCap: 'round',
    },
    colors: ['#4565E1', '#FFA253'],
    series: [70, 70],
    labels: ['Production', 'Return Manual Time'],
    responsive: [{
      breakpoint: 1200,
      options: {
        chart: {
          height: 160
        },
        plotOptions: {
          radialBar: {
            hollow: {
              size: '25%'
            }
          }
        }
      }
    },
  {
      breakpoint: 1199.98,
      options: {
        chart: {
          height: 120
        },
        plotOptions: {
          radialBar: {
            hollow: {
              size: '25%'
            }
          }
        }
      }
    }]
  };

  var chart = new ApexCharts(
    document.querySelector("#production_chart"),
    radialChart
  );
  chart.render();
}

// Task

if ($('#task-overview').length > 0) {
  const options1 = {
        series: [165, 496, 127],
        labels: ["Ongoing", "On hold", "Completed"],
        chart: {
            height: 214,
            type: 'donut',
        },
        dataLabels: {
            enabled: false,
        },
        legend: {
            show: false,
            position: "bottom",
            markers: {
                size: 5
            }
        },
        stroke: {
            show: true,
            curve: 'smooth',
            lineCap: 'round',
            colors: "#fff",
            width: 0,
            dashArray: 0,
        },
        plotOptions: {
            pie: {
                expandOnClick: false,
                donut: {
                    size: '85%',
                    background: 'transparent',
                    labels: {
                        show: true,
                        name: {
                            show: true,
                            fontSize: '20px',
                            color: '#495057',
                            offsetY: -5
                        },
                        value: {
                            show: true,
                            fontSize: '22px',
                            color: '#1A1A1A',
                            offsetY: 5,
                            fontWeight: 600,
                            formatter: function (val) {
                                return val + "%"
                            }
                        },
                        total: {
                            show: true,
                            showAlways: true,
                            label: 'Total Task',
                            fontSize: '14px',
                            fontWeight: 400,
                            color: '#5F5F5F',
                        }
                    }
                }
            }
        },


        colors: ["var(--secondary)", "var(--purple)", "var(--primary)" ],
    };
    const chart1 = new ApexCharts(document.querySelector("#task-overview"), options1);
    chart1.render();
}

// Membership
if ($('#members-overview').length > 0) {
     const options = {
        series: [{
            name: 'Female',
            data: [80, 50, 40, 90, 80],
        }, {
            name: 'Male',
            data: [40, 76, 80, 40, 60],
        }],
        chart: {
            height: 305,
            type: "radar",
            toolbar: {
                show: false,
            },
        },
        colors: ["#E22871", "#3550DC"],
        stroke: {
            width: 1,
        },
        fill: {
            opacity: 0.1,
        },
        markers: {
            size: 0,
        },
        legend: {
            show: true,
            position: "top",
            markers: {
                size: 4,
                strokeWidth: 0,
            },
			onItemClick: {
				toggleDataSeries: false   // 👈 add here to stop hiding on click
			},
        },
        plotOptions: {
            radar: {
                size: 100,
            }
        },
        labels: ['2025', '2026', '2027', '2028', '2029'],
        xaxis: {
            axisBorder: { show: false },
        },
        yaxis: {
            axisBorder: { show: false },
            tickAmount: 5,
        },
        grid: {
      padding: {
          bottom: -70  // try -10, -20 until it looks right
        }
      }
    };
    const chart = new ApexCharts(document.querySelector("#members-overview"), options);
    chart.render();
  }

if ($('#performance-stats').length > 0) {
    const options2 = {
        series: [{
             name: 'This Year',
            data: [60, 20, 50, 60, 70, 90, 20, 45, 65, 40, 30, 20],
            type: 'bar',
        }, {
            name: 'Sales',
            data: [40, 50, 40, 65, 20, 40, 20, 35, 40, 55, 50, 60],
            type: 'area',
        }],
        chart: {
            height: 305,
            type: 'line',
            toolbar: {
                show: false,
            },
            background: 'none',
            fill: "#fff",
        },
        plotOptions: {
            bar: {
                borderRadius: 2,
                columnWidth: '30%',
            }
        },
        grid: {
            borderColor: "#f1f1f1",
            strokeDashArray: 2,
            xaxis: {
                lines: {
                    show: true
                }
            },
            yaxis: {
                lines: {
                    show: false
                }
            }
        },
        colors: ["var(--primary)", "#FF7F00"],
        background: 'transparent',
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth',
            width: [2, 1.5, 2],
            dashArray: [0, 0, 6]
        },
        legend: {
            show: true,
            position: 'bottom',
            markers: {
                width: 8,
                height: 8,
            },
			onItemClick: {
				toggleDataSeries: false   // 👈 add here to stop hiding on click
			}
        },
        xaxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            show: false,
            axisBorder: {
                show: false,
                color: 'rgba(119, 119, 142, 0.05)',
                offsetX: 0,
                offsetY: 0,
            },
            axisTicks: {
                show: false,
                borderType: 'solid',
                color: 'rgba(119, 119, 142, 0.05)',
                width: 6,
                offsetX: 0,
                offsetY: 0
            },
            labels: {
                rotate: -90,
            }
        },
        fill: {
            type: ['solid', 'gradient', 'solid'],
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.4,
                opacityTo: 0.1,
                stops: [0, 90, 100],
                colorStops: [
                    [
                        {
                            offset: 0,
                            color: "var(--primary-color)",
                            opacity: 1
                        },
                        {
                            offset: 75,
                            color: "var(--primary-color)",
                            opacity: 1
                        },
                        {
                            offset: 100,
                            color: 'var(--primary-color)',
                            opacity: 1
                        }
                    ],
                    [
                        {
                            offset: 0,
                            color: "rgba(255, 73, 205, 0.1)",
                            opacity: 0.1
                        },
                        {
                            offset: 75,
                            color: "rgba(255, 73, 205, 0.1)",
                            opacity: 1
                        },
                        {
                            offset: 100,
                            color: 'rgba(255, 73, 205, 0.2)',
                            opacity: 1
                        }
                    ],
                    [
                        {
                            offset: 0,
                            color: 'var(--primary03)',
                            opacity: 1
                        },
                        {
                            offset: 75,
                            color: 'var(--primary03)',
                            opacity: 0.1
                        },
                        {
                            offset: 100,
                            color: 'var(--primary03)',
                            opacity: 1
                        }
                    ],
                ]
            }
        },
        yaxis: {
            show: false,
            axisBorder: {
                show: false,
            },
            axisTicks: {
                show: false,
            }
        },
        tooltip: {
            x: {
                format: 'dd/MM/yy HH:mm'
            },
        },
        grid: {
        padding: {
          right: -15,
          left: -5
        }
      },
    };
    const chart4 = new ApexCharts(document.querySelector("#performance-stats"), options2);
    chart4.render();
  }

// Task Statistics
if ($('#task-statistics').length > 0) {
     const options = {
        series: [49, 35, 64, 32],
        labels: ["Ongoing Tasks", "To Do Tasks", "Completed", "Incompleted Tasks"],
        chart: {
            height: 228,
            type: 'donut',
        },
        dataLabels: {
            enabled: false,
        },

        legend: {
            show: false,
        },
        stroke: {
            show: true,
            curve: 'smooth',
            lineCap: 'round',
            colors: 'var(--white)',
            width: 3,
            dashArray: 0,
        },
        plotOptions: {
            pie: {
                startAngle: -110,
                endAngle: 110,
                offsetY: 10,
                expandOnClick: false,
                donut: {
                    size: '85%',
                    background: 'transparent',
                    labels: {
                        show: true,
                        name: {
                            show: true,
                            fontSize: '20px',
                            color: '#495057',
                            offsetY: -30
                        },
                        value: {
                            show: true,
                            fontSize: '15px',
                            color: undefined,
                            offsetY: -25,
                            formatter: function (val) {
                                return val + "%"
                            }
                        },
                        total: {
                            show: true,
                            showAlways: true,
                            label: 'Total',
                            fontSize: '22px',
                            fontWeight: 600,
                            color: '#495057',
                        }

                    }
                }
            }
        },
        grid: {
            padding: {
                bottom: -100
            }
        },
        colors: ["var(--primary)", "var(--secondary)", "var(--success)", "var(--danger)"],
    };
    const chart = new ApexCharts(document.querySelector("#task-statistics"), options);
    chart.render();
  }

if ($('#production-statistics').length > 0) {
  const options5 = {
    series: [70, 65],
    chart: {
      height: 200,
      type: 'radialBar',
    },
        legend: {
            show: true,
            position: "top",
            markers: {
                size: 4,
                strokeWidth: 0,
            },
			onItemClick: {
				toggleDataSeries: false   // 👈 add here to stop hiding on click
			  }
        },
    plotOptions: {
      radialBar: {
        offsetY: 0,
        startAngle: 0,
        endAngle: 360,
        hollow: {
          margin: 5,
          size: '50%',
          background: 'var(--white)',
          image: undefined,
        },
        dataLabels: {
          name: {
            show: true,
            fontSize: '20px',
            fontFamily: "Roboto, sans-serif",
            offsetY: 0
          },
          value: {
            show: true,
            fontSize: '22px',
            offsetY: 9,
            fontWeight: 600,
            fontFamily: "Roboto, sans-serif",
            color: "#1A1A1A",
            formatter: function (val) {
              return val + "%";
            }
          },
          total: {
            show: true,
            showAlways: true,
            label: 'Total Hours',
            offsetY: 0,
            fontSize: '14px',
            color: '#5F5F5F',
            fontWeight: 400,
            formatter: function (w) {
              return 254;
            }
          }
        }
      }
    },
    tooltip: {
      enabled: true,  // Ensure tooltips are enabled
      y: {
        formatter: function (val) {
          return val + '%'; // Format the tooltip value as percentage
        }
      }
    },
    stroke: {
      lineCap: 'round'
    },
    grid: {
      padding: {
        bottom: -30,
        top: -10
      }
    },
    colors: ["var(--primary)", "#FFA253"],
    labels: ['Production', 'Manual'],
  };
  const chart5 = new ApexCharts(document.querySelector("#production-statistics"), options5);
  chart5.render();
}



if ($('#category-chart').length > 0) {
    var options = {
      series: [30, 20, 15, 35], // Percentages for each section
      chart: {
          type: 'donut',
          height: 175,
      },
      labels: [ 'Delivery', 'Reservation', 'Take Away', 'Dine'], // Labels for the data
      colors: ['#14B51D', '#FFA80B', '#0D76E1', '#A91CFF'], // Colors from the image
      stroke: {
        width: 0, // Explicitly set stroke width to zero
      },
      plotOptions: {
          pie: {
              donut: {
                  size: '60%',
                  labels: {
                      show: true, // Enable donut labels
                      name: {
                        show: true,
                        offsetY: -10, // Position the label name
                        fontSize: '14px',
                      },
                      value: {
                        show: true,
                        offsetY: 10, // Position the series value
                        color: '#333',
                        fontSize: '24px', // Make the value prominent
                        formatter: function (value) {
                                    // Format the value (e.g., add the '%' sign)
                          return value + '%'; 
                        }
                      },
                      total: {
                          show: false,
                          label: 'Leads',
                          formatter: function (w) {
                              return '589';
                          }
                      }
                  }
              }
          }
      },
      dataLabels: {
        enabled: false
      },
      legend: {
        show: false,
      },
      label: {
        show: false,
      }
  };
  
  var chart = new ApexCharts(document.querySelector("#category-chart"), options);
  chart.render();
}


if ($('#sales-chart').length > 0) {
    var options = {
      series: [40],
      lebels: ['Sales'],
      chart: {
        height: 340,
        type: 'radialBar',
        offsetY: -30,
         sparkline: {
        enabled: true // Removes all default padding and extra space
      },
    },
    plotOptions: {
      radialBar: {
        startAngle: -90,
        endAngle: 90,
        dataLabels: {
          name: {
            fontSize: '16px',
            offsetY: 0
          },
          value: {
            offsetY: -40,
            fontSize: '22px',
            color: undefined,
            formatter: function (val) {
              return val + "%";
            }
          },
          
        }
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
          shade: 'dark',
          shadeIntensity: 0.15,
          inverseColors: false,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 50, 65, 91]
      },
    },
    stroke: {
      dashArray: 4
    },
    labels: ['Sales'],
    grid: {
      padding: {
      bottom: 0,
      top: -20
    }
    },
    colors: ["#FFA80B"],
    };       

    var chart = new ApexCharts(document.querySelector("#sales-chart"), options);
    chart.render();

}

// Revenue Chart
if ($('#revenue-chart').length > 0) {
  var options = {
    series: [{
    name: 'Revenue',
    data: [4, 2, 3.5, 3, 2, 2.8, 3.2]
  }],
  chart: {
    height: 220,
    type: 'bar',
    toolbar: {
      show: false
    }
  },
  plotOptions: {
    bar: {
      borderRadius: 10,
      dataLabels: {
        position: 'top', // top, center, bottom
      },
    }
  },
  dataLabels: {
    enabled: true,
    formatter: function (val) {
      return val + "%";
    },
    offsetY: -20,
    style: {
      fontSize: '12px',
      colors: ["#304758"]
    }
  },
  
  xaxis: {
    categories: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    axisBorder: {
      show: false
    },
    axisTicks: {
      show: false
    },
    crosshairs: {
      fill: {
        type: 'gradient',
        gradient: {
          colorFrom: '#F8F8F8',
          colorTo: '#F8F8F8',
          stops: [0, 100],
          opacityFrom: 0.4,
          opacityTo: 0.5,
        }
      }
    },
    tooltip: {
      enabled: true,
    }
  },
  yaxis: {
    axisBorder: {
      show: false
    },
    axisTicks: {
      show: true,
    },
    labels: {
      show: true,
      formatter: function (val) {
        return val + "k";
      }
    },
    
  
  },
  colors: ['#0D76E1']
  };

  var chart = new ApexCharts(document.querySelector("#revenue-chart"), options);
  chart.render();
}
