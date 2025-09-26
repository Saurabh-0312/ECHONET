import express from 'express';
import { getStakeData } from '../controller/stakeDataController.js';

const Router = express.Router();

Router.post('/stake-data', getStakeData);

export default Router;
