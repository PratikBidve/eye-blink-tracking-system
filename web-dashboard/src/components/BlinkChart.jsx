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
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, TimeScale);

export default function BlinkChart({ blinks }) {
  if (!blinks || blinks.length === 0) {
    return <p>No blink data available.</p>;
  }

  // Sort by timestamp ascending
  const sorted = [...blinks].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const data = {
    labels: sorted.map((b) => b.timestamp),
    datasets: [
      {
        label: 'Blink Count',
        data: sorted.map((b) => b.blink_count),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: true },
      tooltip: { enabled: true },
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
        },
      },
      y: {
        title: {
          display: true,
          text: 'Blink Count',
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ maxWidth: 700, margin: '2em auto' }}>
      <Line data={data} options={options} />
    </div>
  );
} 