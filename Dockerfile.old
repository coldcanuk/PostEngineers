# Use Node.js latest
FROM node:latest

# Set working directory
WORKDIR /app

# Install app dependencies
COPY package*.json ./
RUN npm install

# Bundle app source
COPY . .
RUN rm -f .env

# Start the app
CMD [ "npm", "start" ]