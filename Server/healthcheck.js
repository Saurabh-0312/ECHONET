import http from 'http';

const options = {
  host: 'localhost',
  port: process.env.PORT || 3001,
  timeout: 2000,
  path: '/healthz'
};

const request = http.request(options, (res) => {
  console.log(`Health check status: ${res.statusCode}`);
  process.exit(res.statusCode === 200 ? 0 : 1);
});

request.on('error', (err) => {
  console.error('Health check failed:', err);
  process.exit(1);
});

request.end();