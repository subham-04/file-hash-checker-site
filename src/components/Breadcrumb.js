import React from 'react';
import { HStack, Text, Button } from '@chakra-ui/react';
import { FiHome } from 'react-icons/fi';

const Breadcrumb = ({ currentPage, onNavigate }) => {
  const pages = {
    home: { name: 'Home', icon: FiHome },
    installation: { name: 'Installation Guide', icon: null },
    privacy: { name: 'Privacy & License', icon: null }
  };

  // Show Home, Installation Guide, and Privacy Policy as top-level navigation
  const topLevelPages = ['home', 'installation', 'privacy'];
  
  return (
    <HStack gap="4" fontSize="sm">
      {/* Top-level navigation items */}
      {topLevelPages.map((pageKey) => {
        const page = pages[pageKey];
        const isActive = pageKey === currentPage;
        const Icon = page.icon;

        return (
          <HStack key={pageKey} gap="2">
            {!isActive ? (
              <Button
                variant="ghost"
                size="sm"
                leftIcon={Icon ? <Icon /> : undefined}
                onClick={() => onNavigate(pageKey)}
                color="blue.600"
                _dark={{ color: "blue.300" }}
                _hover={{ bg: "blue.50", _dark: { bg: "blue.900" } }}
                h="auto"
                py="1"
                px="2"
              >
                {page.name}
              </Button>
            ) : (
              <Text 
                fontWeight="medium" 
                color="fg" 
                display="flex" 
                alignItems="center" 
                gap="1"
                px="2"
                py="1"
              >
                {Icon && <Icon />}
                {page.name}
              </Text>
            )}
          </HStack>
        );
      })}
    </HStack>
  );
};

export default Breadcrumb;
