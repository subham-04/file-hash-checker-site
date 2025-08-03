# File Hash Checker

A modern, web-based file hash verification tool built with React and Chakra UI. This application provides both a Python desktop application and a web interface for calculating and verifying file hashes using multiple algorithms.

## 🚀 Features

- **Multiple Hash Algorithms**: MD5, SHA1, SHA256
- **VirusTotal Integration**: Optional API integration for malware scanning
- **Modern Web Interface**: Built with React and Chakra UI v3
- **Desktop Application**: Python-based GUI application included
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Dark Theme**: Professional dark mode interface
- **Responsive Design**: Mobile-friendly web interface

## 🌐 Live Demo

Visit the live application: [File Hash Checker](https://subham-04.github.io/file-hash-checker)

## 📦 Installation

### Web Version (Development)

1. Clone the repository:
```bash
git clone https://github.com/subham-04/file-hash-checker.git
cd file-hash-checker
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

### Desktop Version (Python)

1. Download the Python file: [File_Hash_Calculator.py](./public/File_Hash_Calculator.py)

2. Install Python 3.7+ with tkinter support

3. Install required dependencies:
```bash
pip install requests
```

4. Run the application:
```bash
python File_Hash_Calculator.py
```

## 🔧 System Requirements

### Web Version
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection

### Desktop Version
- Windows 10/11, macOS, or Linux
- Python 3.7 or higher
- tkinter (usually included with Python)
- 2GB RAM minimum (4GB recommended)

## 🌟 Usage

### Web Interface
1. Visit the live demo or run locally
2. Navigate through the installation guide
3. Download the Python application
4. Follow the setup instructions

### Desktop Application
1. Launch the Python application
2. Select files to hash
3. Choose hash algorithms
4. Optionally configure VirusTotal integration
5. View and verify hash results

## 🔐 VirusTotal Integration

The application supports optional VirusTotal API integration:

1. Sign up at [virustotal.com](https://www.virustotal.com)
2. Get your free API key (500 requests/day, 15K/month)
3. Configure the API key in the application
4. Enable real-time malware scanning with 40+ antivirus engines

## 🛠️ Built With

- **Frontend**: React 18, Chakra UI v3
- **Desktop**: Python 3, tkinter
- **Icons**: Feather Icons (react-icons/fi)
- **Hosting**: GitHub Pages
- **Build Tool**: Create React App

## 📁 Project Structure

```
file-hash-checker/
├── public/
│   ├── File_Hash_Calculator.py    # Python desktop application
│   └── index.html                 # Web app entry point
├── src/
│   ├── components/
│   │   ├── ui/                    # Chakra UI components
│   │   └── Breadcrumb.js          # Navigation component
│   ├── App.js                     # Main application
│   ├── InstallationGuide.js       # Installation instructions
│   ├── PrivacyPolicy.js           # Privacy and license info
│   └── index.js                   # React entry point
└── package.json                   # Project dependencies
```

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under a Non-Commercial License - see the [Privacy Policy](./src/PrivacyPolicy.js) for details.

**Key Points:**
- ✅ Free for personal, educational, and non-commercial use
- ✅ Modification and distribution allowed for non-commercial purposes
- ❌ Commercial use requires explicit permission
- ❌ No warranty or liability coverage

## 🐛 Bug Reports

Found a bug? Please create an issue with:
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- System information

## 🔒 Security

- All file processing happens locally
- No files are uploaded to external servers
- VirusTotal integration is optional and user-controlled
- Hash calculations are performed client-side

## 📞 Support

- Create an issue on GitHub
- Check the documentation in the app
- Review the installation guide

## 🏆 Acknowledgments

- Chakra UI team for the excellent component library
- VirusTotal for their comprehensive malware scanning API
- React team for the robust framework
- Feather Icons for beautiful iconography

---

**Made with ❤️ for secure file verification**

## Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
