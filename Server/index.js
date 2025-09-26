import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';

import stakeDataRoutes from './routes/stakeDataRoutes.js';
import CidRoutes from './routes/CidRoutes.js'
import ensRoutes from './routes/ensRoutes.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use('/api', stakeDataRoutes);
app.use('/api', CidRoutes);
app.use('/api/ens', ensRoutes);

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
