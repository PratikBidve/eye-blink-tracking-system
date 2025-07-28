import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  TimeScale,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, TimeScale, Filler);

export default function BlinkChart({ blinks }) {
  if (!blinks || blinks.length === 0) {
    return <p style={{textAlign: 'center', marginTop: '2em'}}>No blink data available.</p>;
  }

  // Sort by timestamp ascending
  const sorted = [...blinks].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  // Create a gradient fill for the chart
  const chartRef = React.useRef();
  const getGradient = (ctx, chartArea) => {
    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, 'rgba(75,192,192,0.08)');
    gradient.addColorStop(1, 'rgba(75,192,192,0.35)');
    return gradient;
  };

  const data = {
    labels: sorted.map((b) => b.timestamp),
    datasets: [
      {
        label: 'Blink Count',
        data: sorted.map((b) => b.blink_count),
        fill: true,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return null;
          return getGradient(ctx, chartArea);
        },
        tension: 0.35,
        pointRadius: 6,
        pointHoverRadius: 10,
        pointBackgroundColor: 'rgb(75, 192, 192)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        borderWidth: 3,
        shadowOffsetX: 0,
        shadowOffsetY: 2,
        shadowBlur: 8,
        shadowColor: 'rgba(75,192,192,0.2)'
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        enabled: true,
        backgroundColor: '#222',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgb(75,192,192)',
        borderWidth: 2,
        cornerRadius: 10,
        padding: 14,
        displayColors: false,
        titleFont: { size: 15, weight: 'bold' },
        bodyFont: { size: 14 },
        callbacks: {
          label: function(context) {
            return `Blinks: ${context.parsed.y}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'minute',
          tooltipFormat: 'PPpp',
        },
        title: {
          display: true,
          text: 'Timestamp',
          color: '#333',
          font: { weight: 'bold', size: 15 },
        },
        grid: {
          color: 'rgba(200,200,200,0.08)',
        },
        ticks: {
          color: '#666',
          font: { size: 13 },
        },
      },
      y: {
        title: {
          display: true,
          text: 'Blink Count',
          color: '#333',
          font: { weight: 'bold', size: 15 },
        },
        beginAtZero: true,
        grid: {
          color: 'rgba(200,200,200,0.13)',
        },
        ticks: {
          color: '#666',
          font: { size: 13 },
        },
      },
    },
    layout: {
      padding: {
        top: 20,
        bottom: 20,
        left: 10,
        right: 10,
      },
    },
  };

  return (
    <div style={{ maxWidth: 800, margin: '2em auto', background: '#fff', borderRadius: 16, boxShadow: '0 2px 16px rgba(0,0,0,0.07)', padding: '2em', minHeight: 400 }}>
      <h2 style={{ textAlign: 'center', marginBottom: 24, color: '#222', fontWeight: 700, letterSpacing: 1 }}>Blink Data Over Time</h2>
      <div style={{ height: 350 }}>
        <Line ref={chartRef} data={data} options={options} />
      </div>
    </div>
  );
} 