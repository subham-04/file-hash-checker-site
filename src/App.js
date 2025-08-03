import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  HStack,
  VStack,
  Icon,
  Badge,
  Separator,
  SimpleGrid
} from '@chakra-ui/react';
import { Card } from './components/ui/card';
import InstallationGuide from './InstallationGuide';
import PrivacyPolicy from './PrivacyPolicy';
import Breadcrumb from './components/Breadcrumb';
import StructuredData from './components/StructuredData';
import { 
  FiShield, 
  FiHash, 
  FiUpload, 
  FiCheck, 
  FiLock, 
  FiDatabase,
  FiDownload,
  FiFileText,
  FiSearch,
  FiCpu,
  FiGlobe,
  FiZap
} from 'react-icons/fi';

const FeatureCard = ({ icon, title, description, color = "blue" }) => (
  <Card height="100%">
    <Card.Body>
      <VStack align="start" gap="3">
        <Box p="2" bg={`${color}.50`} borderRadius="md" _dark={{ bg: `${color}.900` }}>
          <Icon fontSize="xl" color={`${color}.500`}>
            {icon}
          </Icon>
        </Box>
        <Heading size="sm">{title}</Heading>
        <Text fontSize="sm" color="fg.muted">
          {description}
        </Text>
      </VStack>
    </Card.Body>
  </Card>
);

const StatCard = ({ title, value, description, details, color = "blue" }) => (
  <Card 
    maxW="xs" 
    mx="auto"
    _hover={{ 
      transform: "translateY(-2px)", 
      shadow: "lg",
      borderColor: `${color}.300`,
      transition: "all 0.3s ease"
    }}
    cursor="pointer"
    transition="all 0.3s ease"
  >
    <Card.Body p="6" textAlign="center">
      <VStack gap="3">
        <Box 
          p="3" 
          bg={`${color}.50`} 
          borderRadius="lg" 
          _dark={{ bg: `${color}.900` }}
          _hover={{ 
            bg: `${color}.100`,
            _dark: { bg: `${color}.800` }
          }}
          transition="all 0.3s ease"
        >
          <Text fontSize="xl" fontWeight="bold" color={`${color}.500`} lineHeight="1">
            {value}
          </Text>
        </Box>
        <VStack gap="1">
          <Text fontSize="md" fontWeight="bold" color="fg">
            {title}
          </Text>
          <Text fontSize="sm" color="fg.muted" fontWeight="medium">
            {description}
          </Text>
          {details && (
            <Text fontSize="xs" color="fg.muted" textAlign="center" lineHeight="tight">
              {details}
            </Text>
          )}
        </VStack>
      </VStack>
    </Card.Body>
  </Card>
);

const UseCaseCard = ({ icon, title, description }) => (
  <Card>
    <Card.Body>
      <HStack gap="3">
        <Icon fontSize="lg" color="purple.500">
          {icon}
        </Icon>
        <Box>
          <Text fontWeight="medium" fontSize="sm">
            {title}
          </Text>
          <Text fontSize="xs" color="fg.muted">
            {description}
          </Text>
        </Box>
      </HStack>
    </Card.Body>
  </Card>
);

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const navigateToPage = (page) => {
    setCurrentPage(page);
  };

  // SEO: Update document title based on current page
  useEffect(() => {
    const titles = {
      home: 'File Hash Checker - Free Hash Calculator & Malware Scanner | MD5 SHA1 SHA256',
      installation: 'Installation Guide - File Hash Checker | Setup Instructions',
      privacy: 'Privacy Policy & License - File Hash Checker | Terms of Use'
    };
    
    document.title = titles[currentPage] || titles.home;
    
    // Update meta description based on page
    const descriptions = {
      home: 'Free file hash calculator with MD5, SHA1, SHA256 algorithms and VirusTotal integration for malware scanning. Download Python desktop app.',
      installation: 'Step-by-step installation guide for File Hash Checker. Download Python desktop application and setup VirusTotal integration.',
      privacy: 'Privacy policy and licensing terms for File Hash Checker. Non-commercial use allowed with proper attribution.'
    };
    
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute('content', descriptions[currentPage] || descriptions.home);
    }
  }, [currentPage]);

  if (currentPage === 'installation') {
    return <InstallationGuide onNavigate={navigateToPage} />;
  }

  if (currentPage === 'privacy') {
    return <PrivacyPolicy onNavigate={navigateToPage} />;
  }

  return (
    <Box minH="100vh" bg="bg.canvas">
      <StructuredData />
      {/* Header */}
      <Box as="header" borderBottomWidth="1px" borderColor="border">
        <Container maxW="7xl" py="4">
          <Flex justify="space-between" align="center">
            <HStack gap="3">
              <Box p="2" bg="blue.500" borderRadius="md">
                <Icon fontSize="xl" color="white">
                  <FiShield />
                </Icon>
              </Box>
              <Box>
                <Heading size="lg" color="blue.600" _dark={{ color: "blue.300" }}>
                  File Hash Checker
                </Heading>
                <Text fontSize="sm" color="fg.muted">
                  Secure File Analysis & Verification
                </Text>
              </Box>
            </HStack>
          </Flex>
          
          {/* Breadcrumb Navigation */}
          <Box pt="4" borderTopWidth="1px" borderColor="border.subtle" mt="4">
            <Breadcrumb currentPage="home" onNavigate={navigateToPage} />
          </Box>
        </Container>
      </Box>

      {/* Hero Section */}
      <Box bg="blue.50" _dark={{ bg: "blue.950" }}>
        <Container maxW="7xl" py="20">
          <VStack gap="8" textAlign="center">
            <VStack gap="4">
              <Badge colorPalette="blue" variant="subtle" px="3" py="1">
                🔒 Enterprise-Grade Security
              </Badge>
              <Heading size="4xl" lineHeight="tight">
                Calculate File Hashes with{' '}
                <Text as="span" color="blue.500">
                  VirusTotal Integration
                </Text>
              </Heading>
              <Text fontSize="xl" color="fg.muted" maxW="2xl">
                A powerful desktop application for calculating MD5, SHA1, SHA256, and SHA512 hashes 
                with comprehensive security analysis using 40+ antivirus engines.
              </Text>
            </VStack>
            
            <HStack gap="4">
              <Button 
                size="lg" 
                colorPalette="blue"
                as="a"
                href="/File_Hash_Calculator.py"
                download="File_Hash_Calculator.py"
              >
                <FiDownload />
                Download
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                as="a"
                href="https://github.com/subham-04/file-hash-checker"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FiGlobe />
                View on GitHub
              </Button>
            </HStack>

            <SimpleGrid columns={{ base: 1, md: 3 }} gap="8" w="full" maxW="4xl">
              <StatCard 
                title="Hash Algorithms" 
                value="3" 
                description="Supported Types"
                details="MD5, SHA1, SHA256 with real-time calculation"
                color="blue"
              />
              <StatCard 
                title="Antivirus Engines" 
                value="40+" 
                description="VirusTotal Integration"
                details="Comprehensive threat analysis with industry-leading detection"
                color="red"
              />
              <StatCard 
                title="Processing Speed" 
                value="1000+" 
                description="Files per Minute"
                details="High-performance batch processing for small files"
                color="green"
              />
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxW="7xl" py="20">
        <VStack gap="12">
          <VStack gap="4" textAlign="center">
            <Heading size="2xl">Key Features</Heading>
            <Text fontSize="lg" color="fg.muted" maxW="2xl">
              Everything you need for secure file verification and malware analysis in one powerful application.
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap="6">
            <FeatureCard
              icon={<FiHash />}
              title="Multi-Hash Support"
              description="Calculate MD5, SHA1, SHA256, and SHA512 hashes for comprehensive file verification."
              color="blue"
            />
            <FeatureCard
              icon={<FiShield />}
              title="VirusTotal Integration"
              description="Analyze files with 40+ antivirus engines for complete security assessment."
              color="red"
            />
            <FeatureCard
              icon={<FiUpload />}
              title="Drag & Drop Interface"
              description="Intuitive file selection with modern dark/light theme and tabbed interface."
              color="green"
            />
            <FeatureCard
              icon={<FiDatabase />}
              title="Batch Processing"
              description="Process files and folders recursively with real-time progress, pause/resume/stop controls."
              color="purple"
            />
            <FeatureCard
              icon={<FiFileText />}
              title="CSV Export"
              description="Export results with timestamps for documentation and compliance tracking."
              color="orange"
            />
            <FeatureCard
              icon={<FiLock />}
              title="Secure Storage"
              description="Windows Registry-based API key management with zero data collection or tracking."
              color="teal"
            />
          </SimpleGrid>
        </VStack>
      </Container>

      {/* Use Cases Section */}
      <Box bg="bg.subtle">
        <Container maxW="7xl" py="20">
          <VStack gap="16">
            <VStack gap="4" textAlign="center">
              <Heading size="2xl">Perfect For</Heading>
              <Text fontSize="lg" color="fg.muted" maxW="2xl">
                Trusted by security professionals, IT administrators, and developers worldwide.
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 2 }} gap="4">
              <UseCaseCard
                icon={<FiShield />}
                title="Security Analysts"
                description="Malware analysis and file verification for incident response"
              />
              <UseCaseCard
                icon={<FiCpu />}
                title="IT Administrators"
                description="System integrity monitoring and software verification"
              />
              <UseCaseCard
                icon={<FiSearch />}
                title="Incident Response"
                description="Digital forensics and investigation with chain of custody"
              />
              <UseCaseCard
                icon={<FiCheck />}
                title="Quality Assurance"
                description="Software testing, build verification, and duplicate detection"
              />
            </SimpleGrid>

            {/* System Requirements & Performance */}
            <VStack gap="12" w="full" pt="8">
              <SimpleGrid columns={{ base: 1, lg: 2 }} gap="8" w="full">
                {/* System Requirements */}
                <Card>
                  <Card.Body p="8">
                    <VStack align="start" gap="6">
                      <HStack gap="3">
                        <Box p="2" bg="blue.50" borderRadius="md" _dark={{ bg: "blue.900" }}>
                          <Icon fontSize="lg" color="blue.500">
                            <FiCpu />
                          </Icon>
                        </Box>
                        <Heading size="lg">System Requirements</Heading>
                      </HStack>
                      
                      <VStack align="start" gap="3" w="full">
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">OS:</Text>
                          <Text fontSize="sm" fontWeight="medium">Windows 10/11</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Python:</Text>
                          <Text fontSize="sm" fontWeight="medium">3.7+ with tkinter</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">RAM:</Text>
                          <Text fontSize="sm" fontWeight="medium">2GB recommended</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Storage:</Text>
                          <Text fontSize="sm" fontWeight="medium">50MB free space</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Internet:</Text>
                          <Text fontSize="sm" fontWeight="medium">For VirusTotal only</Text>
                        </HStack>
                      </VStack>
                    </VStack>
                  </Card.Body>
                </Card>

                {/* Performance Metrics */}
                <Card>
                  <Card.Body p="8">
                    <VStack align="start" gap="6">
                      <HStack gap="3">
                        <Box p="2" bg="green.50" borderRadius="md" _dark={{ bg: "green.900" }}>
                          <Icon fontSize="lg" color="green.500">
                            <FiZap />
                          </Icon>
                        </Box>
                        <Heading size="lg">Performance</Heading>
                      </HStack>
                      
                      <VStack align="start" gap="3" w="full">
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Small files (&lt;1MB):</Text>
                          <Text fontSize="sm" fontWeight="medium">~1000 files/min</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Medium files (1-10MB):</Text>
                          <Text fontSize="sm" fontWeight="medium">~200 files/min</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Large files (&gt;100MB):</Text>
                          <Text fontSize="sm" fontWeight="medium">~10 files/min</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">Memory usage:</Text>
                          <Text fontSize="sm" fontWeight="medium">~50MB + 20MB/1K files</Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm" color="fg.muted">VirusTotal limits:</Text>
                          <Text fontSize="sm" fontWeight="medium">500/day, 15K/month</Text>
                        </HStack>
                      </VStack>
                    </VStack>
                  </Card.Body>
                </Card>
              </SimpleGrid>
            </VStack>
          </VStack>
        </Container>
      </Box>

      {/* Security & Privacy Section */}
      <Box bg="green.50" _dark={{ bg: "green.950" }}>
        <Container maxW="6xl" py="20">
          <VStack gap="12">
            <VStack gap="4" textAlign="center">
              <Badge colorPalette="green" variant="subtle" fontSize="sm" px="4" py="2">
                🔒 Privacy First
              </Badge>
              <Heading size="2xl">Security & Privacy</Heading>
              <Text fontSize="lg" color="fg.muted" maxW="2xl">
                Your data stays on your machine. We prioritize security and privacy above all.
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 2 }} gap="6">
              <HStack gap="4" p="6" bg="white" borderRadius="lg" shadow="sm" _dark={{ bg: "gray.800" }}>
                <Text fontSize="2xl">✅</Text>
                <VStack align="start" gap="1">
                  <Text fontWeight="medium">Local processing</Text>
                  <Text fontSize="sm" color="fg.muted">All hashes calculated on your machine</Text>
                </VStack>
              </HStack>
              
              <HStack gap="4" p="6" bg="white" borderRadius="lg" shadow="sm" _dark={{ bg: "gray.800" }}>
                <Text fontSize="2xl">✅</Text>
                <VStack align="start" gap="1">
                  <Text fontWeight="medium">No telemetry</Text>
                  <Text fontSize="sm" color="fg.muted">Zero data collection or tracking</Text>
                </VStack>
              </HStack>
              
              <HStack gap="4" p="6" bg="white" borderRadius="lg" shadow="sm" _dark={{ bg: "gray.800" }}>
                <Text fontSize="2xl">✅</Text>
                <VStack align="start" gap="1">
                  <Text fontWeight="medium">Secure storage</Text>
                  <Text fontSize="sm" color="fg.muted">API keys stored in Windows Registry</Text>
                </VStack>
              </HStack>
              
              <HStack gap="4" p="6" bg="white" borderRadius="lg" shadow="sm" _dark={{ bg: "gray.800" }}>
                <Text fontSize="2xl">✅</Text>
                <VStack align="start" gap="1">
                  <Text fontWeight="medium">Data integrity</Text>
                  <Text fontSize="sm" color="fg.muted">Automatic validation and corruption detection</Text>
                </VStack>
              </HStack>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>
      {/* Call to Action Section */}
      <Box bg="gradient-to-b" gradientFrom="bg.canvas" gradientTo="blue.50" _dark={{ gradientTo: "blue.950" }}>
        <Container maxW="4xl" py="20">
          <VStack gap="8" textAlign="center">
            <VStack gap="4">
              <Badge colorPalette="green" variant="subtle" fontSize="sm" px="4" py="2">
                ⚡ Get Started Now
              </Badge>
              <Heading size="2xl" lineHeight="tight">
                Ready to Secure Your Files?
              </Heading>
              <Text fontSize="lg" color="fg.muted" maxW="xl">
                Join thousands of security professionals using File Hash Checker for malware analysis and file verification.
              </Text>
            </VStack>

            <HStack gap="4" flexDirection={{ base: "column", sm: "row" }}>
              <Button 
                size="lg" 
                colorPalette="blue" 
                variant="solid"
                as="a"
                href="/File_Hash_Calculator.py"
                download="File_Hash_Calculator.py"
              >
                <FiDownload />
                Download
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                as="a"
                href="https://github.com/subham-04/file-hash-checker"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FiGlobe />
                View on GitHub
              </Button>
              <Button size="lg" variant="ghost" colorPalette="blue" onClick={() => navigateToPage('installation')}>
                📖 Installation Guide
              </Button>
            </HStack>

            <Text fontSize="sm" color="fg.muted">
              Free for personal, educational, and non-profit use • Cross-platform • Python 3.7+
            </Text>
          </VStack>
        </Container>
      </Box>

      {/* Footer */}
      <Box bg="bg.subtle" borderTopWidth="1px">
        <Container maxW="7xl" py="16">
          <VStack gap="12">
            {/* Main Footer Content */}
            <SimpleGrid columns={{ base: 1, md: 3 }} gap="8" w="full">
              {/* Brand Section */}
              <VStack align="start" gap="4">
                <HStack gap="3">
                  <Box p="2" bg="blue.500" borderRadius="md">
                    <Icon fontSize="lg" color="white">
                      <FiShield />
                    </Icon>
                  </Box>
                  <VStack align="start" gap="0">
                    <Text fontWeight="bold" fontSize="lg">File Hash Checker</Text>
                    <Text fontSize="sm" color="fg.muted">
                      Enterprise-grade security
                    </Text>
                  </VStack>
                </HStack>
                <Text fontSize="sm" color="fg.muted" maxW="sm">
                  A powerful Windows desktop application for calculating file hashes with comprehensive VirusTotal integration.
                </Text>
              </VStack>

              <VStack align="start" gap="4">
                <Text fontWeight="medium">Resources</Text>
                <VStack align="start" gap="2" fontSize="sm">
                  <HStack 
                    gap="2" 
                    color="fg.muted" 
                    _hover={{ color: "blue.500" }} 
                    cursor="pointer"
                    as="a"
                    href="https://github.com/subham-04/file-hash-checker"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <FiGlobe />
                    <Text>GitHub Repository</Text>
                  </HStack>
                  <HStack 
                    gap="2" 
                    color="fg.muted" 
                    _hover={{ color: "blue.500" }} 
                    cursor="pointer"
                    as="a"
                    href="/File_Hash_Calculator.py"
                    download="File_Hash_Calculator.py"
                  >
                    <FiDownload />
                    <Text>Download Latest</Text>
                  </HStack>
                  <HStack 
                    gap="2" 
                    color="fg.muted" 
                    _hover={{ color: "blue.500" }} 
                    cursor="pointer"
                    as="a"
                    href="https://github.com/subham-04/file-hash-checker#readme"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <FiFileText />
                    <Text>Documentation</Text>
                  </HStack>
                  <HStack 
                    gap="2" 
                    color="fg.muted" 
                    _hover={{ color: "blue.500" }} 
                    cursor="pointer"
                    onClick={() => navigateToPage('privacy')}
                  >
                    <FiFileText />
                    <Text>Privacy & License</Text>
                  </HStack>
                </VStack>
              </VStack>
              <VStack align="start" gap="4">
                <Text fontWeight="medium">Support</Text>
                <VStack align="start" gap="2" fontSize="sm">
                  <Text color="fg.muted">📖 Create GitHub issues for bugs</Text>
                  <Text color="fg.muted">💼 Commercial licensing inquiries</Text>
                  <Text color="fg.muted">🔧 Check Python dependencies</Text>
                </VStack>
                <Text fontSize="xs" color="fg.muted" fontStyle="italic">
                  Built with ❤️ for the cybersecurity community
                </Text>
              </VStack>
            </SimpleGrid>

            <Separator />
            
            {/* Bottom Footer */}
            <HStack justify="space-between" w="full" flexDirection={{ base: "column", md: "row" }} gap="4">
              <HStack gap="4" fontSize="sm" color="fg.muted">
                <Text>© 2025 Non-Commercial License</Text>
                <Text>•</Text>
                <Text>Privacy First</Text>
                <Text>•</Text>
                <Text>Zero Telemetry</Text>
              </HStack>
              
              <Text fontSize="sm" color="fg.muted">
                Free for personal, educational, and non-profit use
              </Text>
            </HStack>
          </VStack>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
