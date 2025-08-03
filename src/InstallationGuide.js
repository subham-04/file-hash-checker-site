import React from 'react';
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
  SimpleGrid
} from '@chakra-ui/react';
import { Card } from './components/ui/card';
import Breadcrumb from './components/Breadcrumb';
import { 
  FiShield, 
  FiDownload,
  FiTerminal,
  FiCheckCircle,
  FiAlertCircle,
  FiGlobe
} from 'react-icons/fi';

const StepCard = ({ number, title, description, command, color = "blue" }) => (
  <Card position="relative" overflow="hidden" _hover={{ transform: "translateY(-4px)", transition: "all 0.2s" }}>
    <Box
      position="absolute"
      top="0"
      left="0"
      right="0"
      h="1"
      bg="gradient-to-r"
      gradientFrom={`${color}.400`}
      gradientTo={`${color}.600`}
    />
    <Card.Body p="8">
      <VStack gap="6" textAlign="center">
        {/* Step Number with Enhanced Styling */}
        <Box position="relative">
          <Box
            w="20"
            h="20"
            bg="gradient-to-br"
            gradientFrom={`${color}.400`}
            gradientTo={`${color}.600`}
            borderRadius="full"
            display="flex"
            alignItems="center"
            justifyContent="center"
            shadow="lg"
            _dark={{ shadow: "none", borderWidth: "2px", borderColor: `${color}.500` }}
          >
            <Text fontSize="2xl" fontWeight="bold" color="white">
              {number}
            </Text>
          </Box>
          {/* Decorative Ring */}
          <Box
            position="absolute"
            top="-2"
            left="-2"
            w="24"
            h="24"
            borderRadius="full"
            borderWidth="2px"
            borderColor={`${color}.200`}
            borderStyle="dashed"
            _dark={{ borderColor: `${color}.800` }}
          />
        </Box>
        
        <VStack gap="3">
          <Heading size="lg" color={`${color}.600`} _dark={{ color: `${color}.300` }}>
            {title}
          </Heading>
          <Text color="fg.muted" fontSize="sm" lineHeight="relaxed">
            {description}
          </Text>
        </VStack>

        {/* Code Snippet */}
        {command && (
          <Box
            bg="gray.50"
            p="3"
            borderRadius="md"
            borderWidth="1px"
            borderColor="gray.200"
            w="full"
            _dark={{ bg: "gray.900", borderColor: "gray.700" }}
          >
            <Text fontSize="xs" fontFamily="mono" color="gray.600" _dark={{ color: "gray.400" }}>
              {command}
            </Text>
          </Box>
        )}
      </VStack>
    </Card.Body>
  </Card>
);

const RequirementCard = ({ icon, title, requirement, status = "required" }) => (
  <Card>
    <Card.Body p="6">
      <HStack gap="4">
        <Box p="2" bg="blue.50" borderRadius="md" _dark={{ bg: "blue.900" }}>
          <Icon fontSize="lg" color="blue.500">
            {icon}
          </Icon>
        </Box>
        <VStack align="start" gap="1" flex="1">
          <HStack justify="space-between" w="full">
            <Text fontWeight="medium">{title}</Text>
            <Badge 
              colorPalette={status === "required" ? "red" : "green"} 
              variant="subtle"
              size="sm"
            >
              {status === "required" ? "Required" : "Optional"}
            </Badge>
          </HStack>
          <Text fontSize="sm" color="fg.muted">
            {requirement}
          </Text>
        </VStack>
      </HStack>
    </Card.Body>
  </Card>
);

function InstallationGuide({ onNavigateHome, onNavigate }) {
  const navigateToPage = onNavigate || onNavigateHome;
  
  return (
    <Box minH="100vh" bg="bg.canvas">
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
                  Installation Guide
                </Heading>
                <Text fontSize="sm" color="fg.muted">
                  Get File Hash Checker running in minutes
                </Text>
              </Box>
            </HStack>
          </Flex>
          
          {/* Breadcrumb Navigation */}
          <Box pt="4" borderTopWidth="1px" borderColor="border.subtle" mt="4">
            <Breadcrumb currentPage="installation" onNavigate={navigateToPage} />
          </Box>
        </Container>
      </Box>

      {/* Hero Section */}
      <Box bg="blue.50" _dark={{ bg: "blue.950" }}>
        <Container maxW="6xl" py="16">
          <VStack gap="8" textAlign="center">
            <VStack gap="4">
              <Badge colorPalette="green" variant="subtle" px="4" py="2">
                ⚡ Ready in 3 Steps
              </Badge>
              <Heading size="3xl" lineHeight="tight">
                Installation Guide
              </Heading>
              <Text fontSize="xl" color="fg.muted" maxW="2xl">
                Follow these simple steps to get File Hash Checker running on your Windows system
              </Text>
            </VStack>
          </VStack>
        </Container>
      </Box>

      {/* System Requirements */}
      <Container maxW="6xl" py="16">
        <VStack gap="12">
          <VStack gap="4" textAlign="center">
            <Heading size="2xl">System Requirements</Heading>
            <Text fontSize="lg" color="fg.muted">
              Make sure your system meets these requirements before installation
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2 }} gap="4">
            <RequirementCard
              icon={<FiShield />}
              title="Operating System"
              requirement="Windows 10 or Windows 11 (64-bit recommended)"
              status="required"
            />
            <RequirementCard
              icon={<FiTerminal />}
              title="Python"
              requirement="Python 3.7 or higher with tkinter support"
              status="required"
            />
            <RequirementCard
              icon={<FiCheckCircle />}
              title="Memory"
              requirement="2GB RAM minimum (4GB recommended)"
              status="required"
            />
            <RequirementCard
              icon={<FiGlobe />}
              title="Internet Connection"
              requirement="Required only for VirusTotal integration"
              status="optional"
            />
          </SimpleGrid>
        </VStack>
      </Container>

      {/* Installation Steps */}
      <Box bg="bg.subtle">
        <Container maxW="6xl" py="20">
          <VStack gap="16">
            <VStack gap="4" textAlign="center">
              <Heading size="2xl">Installation Steps</Heading>
              <Text fontSize="lg" color="fg.muted">
                Follow these steps in order to set up File Hash Checker
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 3 }} gap="8" w="full">
              <StepCard
                number="1"
                title="Install Python 3.7+"
                description="Download and install Python 3.7 or higher with tkinter support from python.org"
                command="python --version"
                color="blue"
              />
              <StepCard
                number="2"
                title="Install Dependencies"
                description="Open Command Prompt and install the required Python packages"
                command="pip install requests"
                color="green"
              />
              <StepCard
                number="3"
                title="Download & Run"
                description="Download the application and run it using Python"
                command="python File_Hash_Calculator.py"
                color="purple"
              />
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Troubleshooting */}
      <Container maxW="6xl" py="16">
        <VStack gap="12">
          <VStack gap="4" textAlign="center">
            <Heading size="2xl">Troubleshooting</Heading>
            <Text fontSize="lg" color="fg.muted">
              Common issues and their solutions
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, lg: 2 }} gap="8">
            <Card>
              <Card.Body p="8">
                <VStack align="start" gap="4">
                  <HStack gap="3">
                    <Box p="2" bg="red.50" borderRadius="md" _dark={{ bg: "red.900" }}>
                      <Icon fontSize="lg" color="red.500">
                        <FiAlertCircle />
                      </Icon>
                    </Box>
                    <Heading size="md" color="red.600" _dark={{ color: "red.300" }}>
                      Python Not Found
                    </Heading>
                  </HStack>
                  
                  <VStack align="start" gap="3" w="full">
                    <Text fontSize="sm" color="fg.muted">
                      If you get "python is not recognized" error:
                    </Text>
                    <Box
                      bg="gray.50"
                      p="3"
                      borderRadius="md"
                      borderWidth="1px"
                      w="full"
                      _dark={{ bg: "gray.900", borderColor: "gray.700" }}
                    >
                      <Text fontSize="xs" fontFamily="mono" color="gray.600" _dark={{ color: "gray.400" }}>
                        1. Add Python to PATH during installation<br/>
                        2. Or use: py -3 instead of python
                      </Text>
                    </Box>
                  </VStack>
                </VStack>
              </Card.Body>
            </Card>

            <Card>
              <Card.Body p="8">
                <VStack align="start" gap="4">
                  <HStack gap="3">
                    <Box p="2" bg="yellow.50" borderRadius="md" _dark={{ bg: "yellow.900" }}>
                      <Icon fontSize="lg" color="yellow.500">
                        <FiAlertCircle />
                      </Icon>
                    </Box>
                    <Heading size="md" color="yellow.600" _dark={{ color: "yellow.300" }}>
                      Tkinter Missing
                    </Heading>
                  </HStack>
                  
                  <VStack align="start" gap="3" w="full">
                    <Text fontSize="sm" color="fg.muted">
                      If tkinter is not available:
                    </Text>
                    <Box
                      bg="gray.50"
                      p="3"
                      borderRadius="md"
                      borderWidth="1px"
                      w="full"
                      _dark={{ bg: "gray.900", borderColor: "gray.700" }}
                    >
                      <Text fontSize="xs" fontFamily="mono" color="gray.600" _dark={{ color: "gray.400" }}>
                        Reinstall Python with "tcl/tk and IDLE" option checked
                      </Text>
                    </Box>
                  </VStack>
                </VStack>
              </Card.Body>
            </Card>
          </SimpleGrid>
        </VStack>
      </Container>

      {/* VirusTotal Setup */}
      <Box 
        bg="gradient-to-br" 
        gradientFrom="orange.50" 
        gradientTo="yellow.50" 
        _dark={{ 
          gradientFrom: "orange.950", 
          gradientTo: "yellow.950" 
        }}
        position="relative"
        overflow="hidden"
      >
        {/* Background Pattern */}
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          opacity="0.1"
          backgroundImage="radial-gradient(circle at 25px 25px, orange.500 2px, transparent 0), radial-gradient(circle at 75px 75px, yellow.500 2px, transparent 0)"
          backgroundSize="100px 100px"
        />
        
        <Container maxW="6xl" py="20" position="relative">
          <VStack gap="16">
            <VStack gap="6" textAlign="center">
              <Badge 
                colorPalette="orange" 
                variant="subtle" 
                fontSize="sm" 
                px="6" 
                py="3"
                borderRadius="full"
                bg="orange.100"
                _dark={{ bg: "orange.900" }}
              >
                🔑 Optional Setup
              </Badge>
              <Heading size="3xl" lineHeight="tight">
                VirusTotal Integration
              </Heading>
              <Text fontSize="xl" color="fg.muted" maxW="2xl">
                Enable advanced threat analysis with VirusTotal API for comprehensive security scanning
              </Text>
            </VStack>

            {/* Enhanced Step Cards */}
            <SimpleGrid columns={{ base: 1, md: 3 }} gap="8" w="full">
              {/* Step 1 */}
              <Card>
                <Card.Body p="8">
                  <VStack align="start" gap="4">
                    <HStack gap="3">
                      <Box p="2" bg="blue.50" borderRadius="md" _dark={{ bg: "blue.900" }}>
                        <Icon fontSize="lg" color="blue.500">
                          <Text fontSize="2xl" fontWeight="bold">1</Text>
                        </Icon>
                      </Box>
                      <Heading size="md" color="blue.600" _dark={{ color: "blue.300" }}>
                        Get API Key
                      </Heading>
                    </HStack>
                    
                    <VStack align="start" gap="3" w="full">
                      <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }}>
                        Sign up at virustotal.com and get your free API key:
                      </Text>
                      <Box
                        bg="gray.50"
                        p="3"
                        borderRadius="md"
                        borderWidth="1px"
                        w="full"
                        _dark={{ bg: "gray.900", borderColor: "gray.700" }}
                      >
                        <Text fontSize="xs" fontFamily="mono" color="gray.600" _dark={{ color: "gray.400" }}>
                          📊 500 requests/day<br/>
                          📅 15K requests/month
                        </Text>
                      </Box>
                    </VStack>
                  </VStack>
                </Card.Body>
              </Card>

              {/* Step 2 */}
              <Card>
                <Card.Body p="8">
                  <VStack align="start" gap="4">
                    <HStack gap="3">
                      <Box p="2" bg="green.50" borderRadius="md" _dark={{ bg: "green.900" }}>
                        <Icon fontSize="lg" color="green.500">
                          <Text fontSize="2xl" fontWeight="bold">2</Text>
                        </Icon>
                      </Box>
                      <Heading size="md" color="green.600" _dark={{ color: "green.300" }}>
                        Open VirusTotal Tab
                      </Heading>
                    </HStack>
                    
                    <VStack align="start" gap="3" w="full">
                      <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }}>
                        Launch the app and navigate to the VirusTotal integration tab:
                      </Text>
                      <Box
                        bg="gray.50"
                        p="3"
                        borderRadius="md"
                        borderWidth="1px"
                        w="full"
                        _dark={{ bg: "gray.900", borderColor: "gray.700" }}
                      >
                        <Text fontSize="xs" fontFamily="mono" color="gray.600" _dark={{ color: "gray.400" }}>
                          🔍 Real-time scanning<br/>
                          📊 40+ AV engines
                        </Text>
                      </Box>
                    </VStack>
                  </VStack>
                </Card.Body>
              </Card>

              {/* Step 3 */}
              <Card>
                <Card.Body p="8">
                  <VStack align="start" gap="4">
                    <HStack gap="3">
                      <Box p="2" bg="purple.50" borderRadius="md" _dark={{ bg: "purple.900" }}>
                        <Icon fontSize="lg" color="purple.500">
                          <Text fontSize="2xl" fontWeight="bold">3</Text>
                        </Icon>
                      </Box>
                      <Heading size="md" color="purple.600" _dark={{ color: "purple.300" }}>
                        Set API Key
                      </Heading>
                    </HStack>
                    
                    <VStack align="start" gap="3" w="full">
                      <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }}>
                        Click "🔑 Set API Key" and paste your key in the application:
                      </Text>
                      <Box
                        bg="gray.50"
                        p="3"
                        borderRadius="md"
                        borderWidth="1px"
                        w="full"
                        _dark={{ bg: "gray.900", borderColor: "gray.700" }}
                      >
                        <Text fontSize="xs" fontFamily="mono" color="gray.600" _dark={{ color: "gray.400" }}>
                          🔐 Encrypted storage<br/>
                          📈 Usage tracking
                        </Text>
                      </Box>
                    </VStack>
                  </VStack>
                </Card.Body>
              </Card>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Final CTA */}
      <Container maxW="4xl" py="16">
        <VStack gap="8" textAlign="center">
          <VStack gap="4">
            <Heading size="2xl">Ready to Get Started?</Heading>
            <Text fontSize="lg" color="fg.muted">
              Download File Hash Checker and start securing your files today
            </Text>
          </VStack>

          <HStack gap="4" flexDirection={{ base: "column", sm: "row" }}>
            <Button size="lg" colorPalette="blue">
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

          <Text fontSize="sm" color="fg.muted">
            Need help? Create an issue on GitHub or check our documentation
          </Text>
        </VStack>
      </Container>
    </Box>
  );
}

export default InstallationGuide;
