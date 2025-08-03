import React from 'react';

const StructuredData = () => {
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebApplication",
        "@id": "https://subham-04.github.io/file-hash-checker/#webapp",
        "name": "File Hash Checker",
        "alternateName": "Hash Calculator",
        "description": "Free file hash verification tool with MD5, SHA1, SHA256 algorithms and VirusTotal integration for malware scanning",
        "url": "https://subham-04.github.io/file-hash-checker",
        "applicationCategory": "SecurityApplication",
        "operatingSystem": "Any",
        "browserRequirements": "Requires JavaScript",
        "creator": {
          "@type": "Person",
          "name": "Subham",
          "url": "https://github.com/subham-04"
        },
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "USD"
        },
        "featureList": [
          "MD5 hash calculation",
          "SHA1 hash calculation", 
          "SHA256 hash calculation",
          "VirusTotal API integration",
          "File integrity verification",
          "Malware scanning",
          "Cross-platform support",
          "Dark theme interface"
        ]
      },
      {
        "@type": "SoftwareApplication",
        "@id": "https://subham-04.github.io/file-hash-checker/#desktop-app",
        "name": "File Hash Calculator Desktop",
        "applicationCategory": "SecurityApplication",
        "operatingSystem": ["Windows", "macOS", "Linux"],
        "programmingLanguage": "Python",
        "runtimePlatform": "Python 3.7+",
        "downloadUrl": "https://subham-04.github.io/file-hash-checker/File_Hash_Calculator.py",
        "fileFormat": ".py",
        "description": "Python desktop application for file hash calculation with tkinter GUI",
        "creator": {
          "@type": "Person",
          "name": "Subham",
          "url": "https://github.com/subham-04"
        },
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "USD"
        }
      },
      {
        "@type": "WebSite",
        "@id": "https://subham-04.github.io/file-hash-checker/#website",
        "url": "https://subham-04.github.io/file-hash-checker",
        "name": "File Hash Checker",
        "description": "Free online file hash verification and malware scanning tool",
        "publisher": {
          "@type": "Person",
          "name": "Subham",
          "url": "https://github.com/subham-04"
        },
        "potentialAction": {
          "@type": "SearchAction",
          "target": "https://subham-04.github.io/file-hash-checker/?q={search_term_string}",
          "query-input": "required name=search_term_string"
        }
      },
      {
        "@type": "Organization",
        "@id": "https://subham-04.github.io/file-hash-checker/#organization",
        "name": "File Hash Checker",
        "url": "https://subham-04.github.io/file-hash-checker",
        "logo": "https://subham-04.github.io/file-hash-checker/logo512.png",
        "foundingDate": "2025",
        "description": "Open source file hash verification and security tools",
        "sameAs": [
          "https://github.com/subham-04/file-hash-checker"
        ]
      }
    ]
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
};

export default StructuredData;
