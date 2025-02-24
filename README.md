[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

# Supplies (Procurement Management System)

This Odoo project implements an Odoo 17 solution for supplier registration, RFP creation, and quotation management. It is designed as a containerized application for ease of development and production deployment. This repository includes all necessary Docker, Nginx, and configuration files.

## Table of Contents

- [Supplies (Procurement Management System in Odoo)](#supplies-procurement-management-system-in-odoo)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Dependencies](#dependencies)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Method 1: Build the Image](#method-1-build-the-image)
    - [Method 2: Use Prebuilt Image](#method-2-use-prebuilt-image)
  - [Customization](#customization)
  - [Additional Notes](#additional-notes)
  - [License](#license)

## Overview

This project is built on Odoo 17 and is containerized using Docker. It integrates with Nginx as a reverse proxy to ensure smooth request handling and security. The solution leverages additional Python libraries, including Pydantic 2 and the Pydantic email validator, and depends on the wkhtml2pdf binary. The project is intended to run on Ubuntu 24.

## Dependencies

- **Odoo 17 Source Code**
- **wkhtml2pdf Binary**
- **Ubuntu 24**
- **Additional Python Libraries:**
  - Pydantic 2
  - Pydantic email validator

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git for cloning repositories

## Installation

### Method 1: Build the Image

1. **Clone the Docker Branch:**

   ```bash
   git clone --branch supplies-docker --single-branch git@github.com:BJIT-Academy-24/YSD_B4_ODOO_Roni.git supplies-docker
   ```

2. **Enter the Directory:**

   ```bash
   cd supplies-docker
   ```

3. **Clone the Supplies Repository:**

   Inside the `supplies-docker` directory, run:

   ```bash
   git clone --branch rony_30207_final_project --single-branch git@github.com:BJIT-Academy-24/YSD_B4_ODOO_Roni.git supplies
   ```

4. **Prepare the Enterprise Code:**

   Copy your Odoo 17 enterprise code into the current folder and rename the folder to `enterprise` (as expected by the Dockerfile).

5. **Build the Docker Image:**

   ```bash
   docker-compose build
   ```

6. **Start the Containers:**

   ```bash
   docker-compose up
   ```

### Method 2: Use Prebuilt Image

1. **Clone the Supplies Repository:**

   ```bash
   git clone --branch rony_30207_final_project --single-branch git@github.com:BJIT-Academy-24/YSD_B4_ODOO_Roni.git supplies
   ```

2. **Pull the Prebuilt Image:**

   ```bash
   docker-compose pull
   ```

3. **Run the Containers in Detached Mode:**

   ```bash
   docker-compose up -d
   ```

## Customization

- **Nginx Configuration:**  
  You can customize the `nginx.conf` file to meet your requirements. For production deployment, ensure you configure the server hostname and implement other necessary security optimizations.

- **Odoo Configuration:**  
  The `odoo.conf` file is available for adjustments. Modify it according to your deployment environment or performance needs.

- **Docker Compose:**  
  Feel free to edit the `docker-compose.yml` file to change service configurations, add volumes, or update environment variables.

## Additional Notes

- **Production Deployment:**  
  When deploying to production, it is recommended to review and adjust the Nginx settings for SSL termination, load balancing, and other security measures.

- **Further Customizations:**  
  Users can extend and customize other configuration files and services (such as the Odoo enterprise code and additional libraries) based on their project needs.

## License

This project is licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0). You may not use this file except in compliance with the License. You can obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.html.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
