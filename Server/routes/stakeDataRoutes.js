import express from 'express';
import { getStakeData } from '../controllers/stakeDataController.js';

const Router = express.Router();

Router.post('/stake-data', getStakeData);

export default Router;
